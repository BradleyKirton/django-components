from textwrap import dedent

from django.template import Context, Template
from django.test import SimpleTestCase

from django_components import component

from .django_test_setup import *  # NOQA


class SimpleComponent(component.Component):
    def context(self, variable, variable2="default"):
        return {
            "variable": variable,
            "variable2": variable2,
        }

    def template(self, context):
        return "simple_template.html"

    class Media:
        css = {"all": ["style.css"]}
        js = ["script.js"]


class IffedComponent(SimpleComponent):
    def template(self, context):
        return "iffed_template.html"


class SlottedComponent(component.Component):
    def template(self, context):
        return "slotted_template.html"


class SlottedComponentNoSlots(component.Component):
    def template(self, context):
        return "slotted_template_no_slots.html"


class SlottedComponentWithContext(component.Component):
    def context(self, variable):
        return {"variable": variable}

    def template(self, context):
        return "slotted_template.html"


class ComponentTemplateTagTest(SimpleTestCase):
    def setUp(self):
        # NOTE: component.registry is global, so need to clear before each test
        component.registry.clear()

    def test_single_component_dependencies(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<link href="style.css" type="text/css" media="all" rel="stylesheet">\n"""
            """<script type="text/javascript" src="script.js"></script>"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_single_component_css_dependencies(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_css_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<link href="style.css" type="text/css" media="all" rel="stylesheet">"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_single_component_js_dependencies(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_js_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<script type="text/javascript" src="script.js"></script>"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_single_component(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template(
            '{% load component_tags %}{% component name="test" variable="variable" %}'
        )
        rendered = template.render(Context({}))
        self.assertHTMLEqual(rendered, "Variable: <strong>variable</strong>\n")

    def test_call_component_with_two_variables(self):
        component.registry.register(name="test", component=IffedComponent)

        template = Template(
            "{% load component_tags %}"
            '{% component name="test" variable="variable" variable2="hej" %}'
        )
        rendered = template.render(Context({}))
        expected_outcome = (
            """Variable: <strong>variable</strong>\n"""
            """Variable2: <strong>hej</strong>"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_component_called_with_positional_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template(
            '{% load component_tags %}{% component "test" variable="variable" %}'
        )
        rendered = template.render(Context({}))
        self.assertHTMLEqual(rendered, "Variable: <strong>variable</strong>\n")

    def test_multiple_component_dependencies(self):
        component.registry.register(name="test1", component=SimpleComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<link href="style.css" type="text/css" media="all" rel="stylesheet">\n"""
            """<script type="text/javascript" src="script.js"></script>"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_multiple_component_css_dependencies(self):
        component.registry.register(name="test1", component=SimpleComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_css_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<link href="style.css" type="text/css" media="all" rel="stylesheet">"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))

    def test_multiple_component_js_dependencies(self):
        component.registry.register(name="test1", component=SimpleComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template("{% load component_tags %}{% component_js_dependencies %}")
        rendered = template.render(Context())
        expected_outcome = (
            """<script type="text/javascript" src="script.js"></script>"""
        )
        self.assertHTMLEqual(rendered, dedent(expected_outcome))


class ComponentSlottedTemplateTagTest(SimpleTestCase):
    def setUp(self):
        # NOTE: component.registry is global, so need to clear before each test
        component.registry.clear()

    def test_slotted_template_basic(self):
        component.registry.register(name="test1", component=SlottedComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template(
            """
            {% load component_tags %}
            {% component_block "test1" %}
                {% slot "header" %}
                    Custom header
                {% endslot %}
                {% slot "main" %}
                    {% component "test2" variable="variable" %}
                {% endslot %}
            {% endcomponent_block %}
        """
        )
        rendered = template.render(Context({}))

        self.assertHTMLEqual(
            rendered,
            """
            <custom-template>
                <header>Custom header</header>
                <main>Variable: <strong>variable</strong></main>
                <footer>Default footer</footer>
            </custom-template>
        """,
        )

    def test_slotted_template_with_context_var(self):
        component.registry.register(name="test1", component=SlottedComponentWithContext)

        template = Template(
            """
            {% load component_tags %}
            {% with my_first_variable="test123" %}
                {% component_block "test1" variable="test456" %}
                    {% slot "main" %}
                        {{ my_first_variable }} - {{ variable }}
                    {% endslot %}
                    {% slot "footer" %}
                        {{ my_second_variable }}
                    {% endslot %}
                {% endcomponent_block %}
            {% endwith %}
        """
        )
        rendered = template.render(Context({"my_second_variable": "test321"}))

        self.assertHTMLEqual(
            rendered,
            """
            <custom-template>
                <header>Default header</header>
                <main>test123 - test456</main>
                <footer>test321</footer>
            </custom-template>
        """,
        )

    def test_slotted_template_no_slots_filled(self):
        component.registry.register(name="test", component=SlottedComponent)

        template = Template(
            '{% load component_tags %}{% component_block "test" %}{% endcomponent_block %}'
        )
        rendered = template.render(Context({}))

        self.assertHTMLEqual(
            rendered,
            """
            <custom-template>
                <header>Default header</header>
                <main>Default main</main>
                <footer>Default footer</footer>
            </custom-template>
        """,
        )

    def test_slotted_template_without_slots(self):
        component.registry.register(name="test", component=SlottedComponentNoSlots)
        template = Template(
            """
            {% load component_tags %}
            {% component_block "test" %}{% endcomponent_block %}
        """
        )
        rendered = template.render(Context({}))

        self.assertHTMLEqual(rendered, "<custom-template></custom-template>")
