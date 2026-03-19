"""Check macro arguments match between the manifest and the SQL code."""

from jinja2 import Environment
from jinja2.ext import Extension
from jinja2.nodes import Expr
from jinja2.nodes import Macro as JinjaMacro
from jinja2.nodes import Name
from jinja2.parser import Parser

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import macro_argument_mismatch_manifest_vs_sql
from utils.manifest_object.macro import Macro as ManifestMacro


class Jinja2TestMacroExtension(Extension):
    """Extends the standard Jinja2 tag set with a 'test' tag.

    The 'test' tag is unique to the dbt templating language
    and is not supported in standard Jinja2. Its behaviour
    is very similar to the 'macro' tag, but the 'name' attribute
    is parsed with the prefix 'test_'. There may be other
    differences, but these are not implemented here as they don't
    affect the functioning of this module.

    Attributes:
        tags: set of tag names
    """

    tags = {"test"}

    def parse(self, parser: Parser) -> JinjaMacro:
        """Parse Jinja2 templates for the 'test' tag.

        :param parser: a jinja2.parser.Parser instance
        :return: a jinja2.nodes.Macro instance where the
        name attribute is prefixed with 'test_'
        """
        lineno = next(parser.stream).lineno
        name_token = parser.stream.expect("name")
        macro_name = f"test_{name_token.value}"
        args: list[Name] = []
        defaults: list[Expr] = []
        parser.stream.expect("lparen")
        while parser.stream.current.type != "rparen":
            if args:
                parser.stream.expect("comma")
            arg = parser.parse_assign_target(name_only=True)
            arg.set_ctx("param")
            args.append(arg)
        parser.stream.expect("rparen")
        body = parser.parse_statements(("name:endtest",), drop_needle=True)
        macro = JinjaMacro(macro_name, args, defaults, body)
        macro.set_lineno(lineno)
        return macro


def get_macro_args_from_sql_code(macro: ManifestMacro) -> set[str]:
    """Get the names of all a macro's arguments from the SQL code.

    Checking YAML files alone for macros where arguments are listed
    but don't have descriptions is not enough, because it's possible
    to list a macro without listing its arguments at all.

    Args:
        macro: a dictionary of macro data from the dbt manifest.json
    Returns:
        a set of macro argument names belonging to the macro
    """
    env = Environment()
    env.add_extension(Jinja2TestMacroExtension)
    body = env.parse(macro.macro_sql).body
    for item in body:
        macro_key = macro.unique_id.split(".")[-1]
        if isinstance(item, JinjaMacro) and item.name == macro_key:
            return {arg.name for arg in item.args}
    return set()


class MacroArgumentsMatchManifestVsSql(ManifestCheck):
    """Check macro arguments match between the manifest and the SQL code.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
        sql_args: Collection of macro argument names from the SQL code
        manifest_args: Collection of macro argument names from the manifest file
    """

    manifest_args: set[str] = set()
    sql_args: set[str] = set()
    check_name: str = "macro-arguments-match-manifest-vs-sql"
    additional_arguments = [
        "include_packages",
        "include_tags",
        "exclude_packages",
        "exclude_tags",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        macros = self.manifest.in_scope_macros
        sql_args = set()
        manifest_args = set()
        for macro in macros:
            for sql_arg in get_macro_args_from_sql_code(macro):
                sql_args.add(f"{macro.unique_id}.{sql_arg}")
            for manifest_arg in macro.arguments:
                manifest_args.add(f"{macro.unique_id}.{manifest_arg.name}")
        self.manifest_args = manifest_args
        self.sql_args = sql_args

    @property
    def has_failures(self) -> bool:
        """Determine whether any entities failed the check."""
        return self.manifest_args != self.sql_args

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return macro_argument_mismatch_manifest_vs_sql(
            sql_args=self.sql_args, manifest_args=self.manifest_args
        )
