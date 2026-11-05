import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_profile_readme.py"
GIF = "https://media0.giphy.com/media/A9mRuRtTa6wYHQgVVi/giphy.gif"
PINNED_PROJECTS = (
    ("Solythis-DnD", "https://github.com/Nothrovo/Solythis-DnD"),
    ("Damsel-and-Desire", "https://github.com/Nothrovo/Damsel-and-Desire"),
    ("Arbiter", "https://github.com/Nothrovo/Arbiter"),
    ("Neuropetra-IP", "https://github.com/Nothrovo/Neuropetra-IP"),
    ("DIPTERA", "https://github.com/HETSHI-PLAY/DIPTERA"),
)


def valid_readme() -> str:
    return f"""# Hadi Nurhasan Darma — Nothrovo

<img src="{GIF}" width="440" alt="Bomb Devil explosion" />

Cyber SOC Analyst and Web Developer.

<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&amp;lines=Evidence+first.+Detonate." alt="Atmospheric typing signal" />

## Selected Work

### [Solythis-DnD](https://github.com/Nothrovo/Solythis-DnD)
### [Damsel-and-Desire](https://github.com/Nothrovo/Damsel-and-Desire)
### [Arbiter](https://github.com/Nothrovo/Arbiter)
### [Neuropetra-IP](https://github.com/Nothrovo/Neuropetra-IP)
### [DIPTERA](https://github.com/HETSHI-PLAY/DIPTERA)

[Email](mailto:hadinurhasandarma@gmail.com) · [GitHub](https://github.com/Nothrovo) · [LinkedIn](https://www.linkedin.com/in/hadind)
"""


class ValidatorTests(unittest.TestCase):
    def run_validator(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(readme)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_accepts_compliant_readme(self):
        result = self.run_validator(valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_style_detection_allows_markdown_image_query_but_rejects_html_attribute(self):
        badge = "![Useful badge](https://img.shields.io/badge/test-pass?style=for-the-badge)"
        result = self.run_validator(valid_readme() + f"\n{badge}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        result = self.run_validator(valid_readme() + '\n<div style="color:red">x</div>\n')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("forbidden HTML/CSS", result.stdout)

    def test_rejects_each_forbidden_or_missing_constraint(self):
        cases = {
            "explosion GIF must be the first image": valid_readme().replace(
                f'<img src="{GIF}" width="440" alt="Bomb Devil explosion" />',
                f'![Other](https://example.com/first.png)\n\n<img src="{GIF}" width="440" alt="Bomb Devil explosion" />',
            ),
            "exactly one GIF": valid_readme().replace(
                "Cyber SOC Analyst", "![Extra](https://example.com/extra.gif)\n\nCyber SOC Analyst"
            ),
            "streak-stats": valid_readme() + "\nhttps://github-readme-streak-stats.herokuapp.com/x\n",
            "manual <br>": valid_readme() + "\n<br>\n",
            "img.shields.io": valid_readme()
            + "\n"
            + "![Useful badge](https://img.shields.io/badge/x-y)\n" * 19,
            "stats cards are forbidden": valid_readme()
            + "\n![GitHub statistics](https://github-readme-stats.vercel.app/api?username=Nothrovo)\n",
            "native Markdown H1": valid_readme().replace("# Hadi Nurhasan Darma — Nothrovo", "<h1>Hadi Nurhasan Darma — Nothrovo</h1>"),
            "Cyber SOC Analyst": valid_readme().replace("Cyber SOC Analyst", "SOC Analyst"),
            "Web Developer": valid_readme().replace("Web Developer", "Developer"),
            "Selected Work must contain exactly five unique required Markdown H3 project links": valid_readme().replace(
                "### [Solythis-DnD](https://github.com/Nothrovo/Solythis-DnD)\n", ""
            ),
            "MedChain project link is forbidden": valid_readme()
            + "\n[MedChain](https://github.com/Nothrovo/MedChain)\n",
            "meaningful nonempty alt": valid_readme().replace('alt="Bomb Devil explosion"', 'alt=""'),
            "forbidden HTML/CSS": valid_readme() + "\n<div style=\"color:red\">x</div>\n",
            "table markup": valid_readme() + "\n<table><tr><td>x</td></tr></table>\n",
            "mailto": valid_readme().replace(
                "mailto:hadinurhasandarma@gmail.com", "https://example.com/email"
            ),
            "GitHub Nothrovo": valid_readme().replace("[GitHub](https://github.com/Nothrovo)", "[GitHub](https://github.com/other)"),
            "LinkedIn /in/hadind": valid_readme().replace("/in/hadind", "/in/other"),
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout + result.stderr)

    def test_requires_one_path_argument(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True, check=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", (result.stdout + result.stderr).lower())

    def test_rejects_roles_confined_to_image_alt_text(self):
        text = valid_readme().replace(
            "![Bomb Devil explosion]", "![Cyber SOC Analyst and Web Developer explosion]"
        ).replace("Cyber SOC Analyst and Web Developer.", "Security and software professional.")
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("native text must contain Cyber SOC Analyst", result.stdout)
        self.assertIn("native text must contain Web Developer", result.stdout)

    def test_rejects_unlinked_project_names_and_plain_exact_urls(self):
        text = valid_readme()
        for project, url in PINNED_PROJECTS:
            text = text.replace(
                f"[{project}]({url})",
                f"{project}: {url}",
            )
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Selected Work must contain exactly five unique required Markdown H3 project links", result.stdout)

    def test_rejects_single_character_image_alt(self):
        result = self.run_validator(valid_readme().replace("Bomb Devil explosion", "x"))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("meaningful nonempty alt", result.stdout)

    def test_rejects_raw_unlinked_contact_urls(self):
        text = valid_readme().replace(
            "[Email](mailto:hadinurhasandarma@gmail.com) · "
            "[GitHub](https://github.com/Nothrovo) · "
            "[LinkedIn](https://www.linkedin.com/in/hadind)",
            "mailto:hadinurhasandarma@gmail.com · https://github.com/Nothrovo · "
            "https://www.linkedin.com/in/hadind",
        )
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mailto email link is required", result.stdout)
        self.assertIn("GitHub Nothrovo profile link is required", result.stdout)
        self.assertIn("LinkedIn /in/hadind link is required", result.stdout)

    def test_rejects_multiple_html_anchors_when_first_is_unclosed(self):
        text = valid_readme().replace(
            "[Email](mailto:hadinurhasandarma@gmail.com) · "
            "[GitHub](https://github.com/Nothrovo)",
            '<a href="mailto:hadinurhasandarma@gmail.com">Email · '
            '<a href="https://github.com/Nothrovo">GitHub</a>',
        )
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("HTML anchors are unsupported; use inline Markdown links", result.stdout)

    def test_markdown_links_inside_unrelated_html_attributes_do_not_count(self):
        project_block = "\n".join(f"### [{name}]({url})" for name, url in PINNED_PROJECTS)
        contact_block = valid_readme().splitlines()[-1]
        hidden_links = project_block + " " + contact_block
        text = valid_readme().replace(project_block, "Arbiter, Neuropetra-IP, and MedChain")
        text = text.replace(contact_block, f'<span title="{hidden_links}">Contacts</span>')
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Selected Work must contain exactly five unique required Markdown H3 project links", result.stdout)
        self.assertIn("mailto email link is required", result.stdout)
        self.assertIn("GitHub Nothrovo profile link is required", result.stdout)
        self.assertIn("LinkedIn /in/hadind link is required", result.stdout)

    def test_rejects_active_html_anchor_with_clear_inline_markdown_guidance(self):
        text = valid_readme() + '\n<a href="https://example.com">Example</a>\n'
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        message = "HTML anchors are unsupported; use inline Markdown links"
        self.assertIn(message, result.stdout)
        self.assertEqual(result.stdout.count(message), 1)

    def test_hidden_source_cannot_satisfy_visible_requirements(self):
        hidden_identity = {
            "fenced code": "# Different Name\n\n```md\n# Hadi Nurhasan Darma — Nothrovo\n```",
            "comment": "# Different Name\n\n<!-- # Hadi Nurhasan Darma — Nothrovo -->",
        }
        for label, replacement in hidden_identity.items():
            with self.subTest(kind=label, requirement="identity"):
                result = self.run_validator(
                    valid_readme().replace("# Hadi Nurhasan Darma — Nothrovo", replacement)
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("native Markdown H1", result.stdout)

        hidden_roles = {
            "comment": "<!-- Cyber SOC Analyst and Web Developer -->",
            "fence": "```\nCyber SOC Analyst and Web Developer\n```",
            "inline code": "`Cyber SOC Analyst and Web Developer`",
            "quoted HTML attribute": '<span title="Cyber SOC Analyst > Web Developer">professional</span>',
        }
        for label, replacement in hidden_roles.items():
            with self.subTest(kind=label, requirement="roles"):
                result = self.run_validator(
                    valid_readme().replace("Cyber SOC Analyst and Web Developer.", replacement)
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("native text must contain Cyber SOC Analyst", result.stdout)
                self.assertIn("native text must contain Web Developer", result.stdout)

    def test_links_in_fences_and_comments_do_not_count(self):
        replacements = {
            "fence": lambda value: f"```md\n{value}\n```",
            "comment": lambda value: f"<!-- {value} -->",
        }
        project_block = "\n".join(f"### [{name}]({url})" for name, url in PINNED_PROJECTS)
        contact_block = valid_readme().splitlines()[-1]
        for label, hide in replacements.items():
            with self.subTest(kind=label, links="projects"):
                result = self.run_validator(valid_readme().replace(project_block, hide(project_block)))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Selected Work must contain exactly five unique required Markdown H3 project links", result.stdout)
            with self.subTest(kind=label, links="contacts"):
                result = self.run_validator(valid_readme().replace(contact_block, hide(contact_block)))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("mailto email link is required", result.stdout)

    def test_hidden_images_and_markup_do_not_affect_active_limits(self):
        prefix = (
            "```md\n![Hidden first](https://example.com/first.gif)\n"
            "https://readme-typing-svg.example/x <br><br><br>\n```\n"
            "<!-- ![Hidden](https://img.shields.io/x.gif) "
            "https://github-readme-streak-stats.example/x <br><br><br> -->\n"
        )
        result = self.run_validator(prefix + valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_image_totals_count_only_active_rendered_images(self):
        hidden = "<!-- " + " ".join(
            f"![Hidden badge](https://img.shields.io/badge/hidden-{i})" for i in range(20)
        ) + " -->\n```\n![Hidden stats](https://github-readme-stats.example/api)\n```\n"
        result = self.run_validator(hidden + valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepts_exact_active_limits(self):
        shields = "\n".join(
            f"![Useful badge {i}](https://img.shields.io/badge/item-{i})" for i in range(18)
        )
        result = self.run_validator(valid_readme() + f"\n{shields}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_requires_exact_final_contract_details(self):
        typing = '<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&amp;lines=Evidence+first.+Detonate." alt="Atmospheric typing signal" />'
        solythis = "### [Solythis-DnD](https://github.com/Nothrovo/Solythis-DnD)"
        cases = {
            "typing SVG zero": valid_readme().replace(typing + "\n\n", ""),
            "typing SVG two": valid_readme() + "\n" + typing,
            "typing SVG wrong font": valid_readme().replace("font=Space+Mono", "font=Fira+Code"),
            "typing SVG wrong line": valid_readme().replace("Evidence+first.+Detonate.", "Observe+first."),
            "typing SVG multiple lines": valid_readme().replace("lines=Evidence+first.+Detonate.", "lines=Evidence+first.+Detonate.&amp;lines=Other"),
            "manual <br> one": valid_readme() + "\n<br>",
            "manual <br> two": valid_readme() + "\n<br><br>",
            "width missing": valid_readme().replace('width="440" ', "", 1),
            "width 439": valid_readme().replace('width="440"', 'width="439"', 1),
            "width 441": valid_readme().replace('width="440"', 'width="441"', 1),
            "Selected Work extra": valid_readme() + "\n### [Extra](https://github.com/Nothrovo/Extra)",
            "Selected Work missing": valid_readme().replace(solythis + "\n", ""),
            "Selected Work duplicate": valid_readme().replace(solythis, solythis + "\n" + solythis),
            "Selected Work elsewhere": valid_readme().replace(solythis, "[Solythis-DnD](https://github.com/Nothrovo/Solythis-DnD)"),
        }
        for expected, text in cases.items():
            with self.subTest(case=expected):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected.split()[0], result.stdout)

        hidden = "<!-- <br><br> -->\n```html\n<br><br>\n```\n"
        result = self.run_validator(hidden + valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepts_one_or_two_capsule_images_but_rejects_three(self):
        image = "![Gradient accent {i}](https://capsule-render.vercel.app/api?type=waving&text={i})"
        for count in (1, 2):
            with self.subTest(count=count):
                additions = "\n".join(image.format(i=i) for i in range(count))
                result = self.run_validator(valid_readme() + "\n" + additions)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        additions = "\n".join(image.format(i=i) for i in range(3))
        result = self.run_validator(valid_readme() + "\n" + additions)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("capsule-render images must be <= 2; found 3", result.stdout)

    def test_rejects_roles_confined_to_typing_svg_images(self):
        text = valid_readme().replace(
            "Cyber SOC Analyst and Web Developer.",
            "![Animated roles](https://readme-typing-svg.demolab.com?lines=Cyber+SOC+Analyst;Web+Developer)",
        )
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("native text must contain Cyber SOC Analyst", result.stdout)
        self.assertIn("native text must contain Web Developer", result.stdout)

    def test_rejects_tables_unclosed_anchors_and_meaningless_alts(self):
        cases = {
            "table markup is forbidden": valid_readme() + "\n| A | B |\n|---|---|\n| x | y |\n",
            "mailto email link is required": valid_readme().replace(
                "[Email](mailto:hadinurhasandarma@gmail.com)",
                '<a href="mailto:hadinurhasandarma@gmail.com">Email',
            ),
            "meaningful nonempty alt": valid_readme().replace("Bomb Devil explosion", "xxx"),
            "meaningful nonempty alt ": valid_readme().replace("Bomb Devil explosion", "123"),
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected.strip()):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected.strip(), result.stdout)

    def test_rejects_explicitly_unsupported_source_syntax(self):
        cases = {
            "reference-style Markdown": valid_readme() + "\n![Badge][badge]\n[badge]: https://example.com/badge.png\n",
            "reference-style Markdown ": valid_readme() + "\n[site][home]\n[home]: https://example.com\n",
            "quoted src": valid_readme() + "\n<img src=https://example.com/x.png alt=UsefulBadge>\n",
            "HTML anchors are unsupported": valid_readme() + "\n<a href=https://example.com>site</a>\n",
            "quoted alt": valid_readme() + "\n<img src=\"https://example.com/x.png\" alt=UsefulBadge>\n",
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected.strip()):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected.strip(), result.stdout)

    def test_typing_svg_requires_exact_single_decoded_font_and_lines_values(self):
        cases = {
            "font suffix": valid_readme().replace("font=Space+Mono", "font=Space+MonoBogus"),
            "duplicate font": valid_readme().replace(
                "font=Space+Mono", "font=Space+Mono&amp;font=Fira+Code"
            ),
            "lines suffix": valid_readme().replace(
                "lines=Evidence+first.+Detonate.", "lines=Evidence+first.+Detonate.Bogus"
            ),
            "duplicate lines": valid_readme().replace(
                "lines=Evidence+first.+Detonate.",
                "lines=Evidence+first.+Detonate.&amp;lines=Other",
            ),
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("typing SVG must be exactly one image", result.stdout)

        result = self.run_validator(valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_first_rendered_image_itself_must_be_html_explosion_with_width_440(self):
        explosion_tag = f'<img src="{GIF}" width="440" alt="Bomb Devil explosion" />'
        cases = {
            "markdown explosion before unrelated sized HTML image": valid_readme().replace(
                explosion_tag,
                f'![Bomb Devil explosion]({GIF})\n\n'
                '<img src="https://example.com/unrelated.png" width="440" alt="Unrelated image" />',
            ),
            "first HTML explosion missing width": valid_readme().replace(
                explosion_tag, f'<img src="{GIF}" alt="Bomb Devil explosion" />'
            ),
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                result = self.run_validator(text)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("first explosion GIF HTML image width must be exactly 440", result.stdout)

        result = self.run_validator(valid_readme())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
