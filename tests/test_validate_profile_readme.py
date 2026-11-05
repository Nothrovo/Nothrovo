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

![Bomb Devil explosion]({GIF})

Cyber SOC Analyst and Web Developer.

- [Solythis-DnD](https://github.com/Nothrovo/Solythis-DnD)
- [Damsel-and-Desire](https://github.com/Nothrovo/Damsel-and-Desire)
- [Arbiter](https://github.com/Nothrovo/Arbiter)
- [Neuropetra-IP](https://github.com/Nothrovo/Neuropetra-IP)
- [DIPTERA](https://github.com/HETSHI-PLAY/DIPTERA)

![GitHub stats](https://github-readme-stats.vercel.app/api?username=Nothrovo)

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

    def test_rejects_each_forbidden_or_missing_constraint(self):
        cases = {
            "explosion GIF must be the first image": valid_readme().replace(
                f"![Bomb Devil explosion]({GIF})",
                f"![Other](https://example.com/first.png)\n\n![Bomb Devil explosion]({GIF})",
            ),
            "exactly one GIF": valid_readme().replace(
                "Cyber SOC Analyst", "![Extra](https://example.com/extra.gif)\n\nCyber SOC Analyst"
            ),
            "readme-typing-svg": valid_readme() + "\nhttps://readme-typing-svg.example/x\n",
            "streak-stats": valid_readme() + "\nhttps://github-readme-streak-stats.herokuapp.com/x\n",
            "capsule-render": valid_readme() + "\nhttps://capsule-render.vercel.app/x\n",
            "manual <br>": valid_readme() + "\n<br><br><br>\n",
            "img.shields.io": valid_readme()
            + "\n"
            + "![Useful badge](https://img.shields.io/badge/x-y)\n" * 13,
            "stats cards": valid_readme()
            + "\n![Language statistics](https://github-readme-stats.vercel.app/api/top-langs)\n"
            + "![Pinned repository statistics](https://github-readme-stats.vercel.app/api/pin)\n",
            "native Markdown H1": valid_readme().replace("# Hadi Nurhasan Darma — Nothrovo", "<h1>Hadi Nurhasan Darma — Nothrovo</h1>"),
            "Cyber SOC Analyst": valid_readme().replace("Cyber SOC Analyst", "SOC Analyst"),
            "Web Developer": valid_readme().replace("Web Developer", "Developer"),
            "pinned project links must occur before": valid_readme().replace(
                "![GitHub stats](https://github-readme-stats.vercel.app/api?username=Nothrovo)\n\n", ""
            ).replace(
                "- [Solythis-DnD]", "![GitHub stats](https://github-readme-stats.vercel.app/api?username=Nothrovo)\n\n- [Solythis-DnD]"
            ),
            "MedChain project link is forbidden": valid_readme()
            + "\n[MedChain](https://github.com/Nothrovo/MedChain)\n",
            "meaningful nonempty alt": valid_readme().replace("![Bomb Devil explosion]", "![]"),
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
        self.assertIn("pinned project links must occur before", result.stdout)

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
        project_block = "\n".join(f"- [{name}]({url})" for name, url in PINNED_PROJECTS)
        contact_block = valid_readme().splitlines()[-1]
        hidden_links = project_block + " " + contact_block
        text = valid_readme().replace(project_block, "Arbiter, Neuropetra-IP, and MedChain")
        text = text.replace(contact_block, f'<span title="{hidden_links}">Contacts</span>')
        result = self.run_validator(text)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pinned project links must occur before", result.stdout)
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
        project_block = "\n".join(f"- [{name}]({url})" for name, url in PINNED_PROJECTS)
        contact_block = valid_readme().splitlines()[-1]
        for label, hide in replacements.items():
            with self.subTest(kind=label, links="projects"):
                result = self.run_validator(valid_readme().replace(project_block, hide(project_block)))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("pinned project links must occur before", result.stdout)
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
            f"![Useful badge {i}](https://img.shields.io/badge/item-{i})" for i in range(12)
        )
        extra_stats = "![Language statistics](https://github-readme-stats.vercel.app/api/top-langs)"
        result = self.run_validator(valid_readme() + f"\n<br><br>\n{shields}\n{extra_stats}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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


if __name__ == "__main__":
    unittest.main()
