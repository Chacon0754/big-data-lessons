from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

MAIN__FILE = ROOT / "main.tex"
CONFIG_FILE = ROOT / "config.tex"
BUILD_ROOT = ROOT / "build"

# ===========
#   Utilities
# ===========

def read_file(path: Path) -> str:
    """
        Reads a file using UTF-8
    """
    return path.read_text(encoding="utf-8")

def get_command_value(text: str, command: str) -> str:
    """
        Gets the value of a simple LaTex command.
    """
    pattern = (
        rf"\\(?:newcommand|renewcommand)"
        rf"\{{\\{re.escape(command)}\}}"
        rf"\s*\{{(.*?)\}}"
    )

    match = re.search(
        pattern,
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(f"command \\{command} not found")

    return match.group(1).strip()


def slugify_activity(activity: str) -> str:
    """
        Converts: Activity 1
        in: activity_1
    """
    return (
        activity.strip().lower().replace(" ", "_")
    )

# ===========
#   Reading current activity
# ===========

main_text = read_file(MAIN__FILE)

try:
    actividad_path = get_command_value(main_text, "actividadactual")
except ValueError as error:
    print(f"Error: {error}")
    sys.exit(1)

actividad_dir = ROOT / actividad_path
if not actividad_dir.exists():
    print(f"Folder of activity {actividad_dir} doesn't exist")
    sys.exit(1)

metadata_file = actividad_dir / "metadata.tex"
if not metadata_file.exists():
    print(f"Couldn't find metadata.tex: {metadata_file}")
    sys.exit(1)


# ==========
#   Read metadata
# ==========

metadata_text = read_file(metadata_file)
try:
    codigo = get_command_value(metadata_text, "codigoactividad")
    actividad = get_command_value(metadata_text, "actividad")
except ValueError as error:
    print(f"Error in metadata.tex: {error}")
    sys.exit(1)


# ==========
#   Read general config
# ==========

config_text = read_file(CONFIG_FILE)

try:
    matricula = get_command_value(config_text, "matricula")
except ValueError as error:
    print(f"Error in config.tex: {error}")
    sys.exit(1)


# ==========
#   Name of the final PDF
# ==========

actividad_slug = slugify_activity(actividad)
pdf_name = (f"{codigo}_{actividad_slug}_{matricula}.pdf")


# ==========
#   Generate specific activity build
# ==========

build_dir = BUILD_ROOT / actividad_path

build_dir.mkdir(parents=True, exist_ok=True)



# ==========
#   Compiling
# =========

print()
print("=" * 60)
print("Compiling activity")
print("=" * 60)

print(f"Activity:   {actividad}")
print(f"Code:       {codigo}")
print(f"Build:      {build_dir.relative_to(ROOT)}")

print()

result = subprocess.run(
    [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-file-line-error",
        f"-outdir={build_dir}",
        f"-auxdir={build_dir}",
        "main.tex"
    ],
    cwd=ROOT
)

if result.returncode != 0:
    print()
    print("=" * 60)
    print("COMPILATION ERROR")
    print("=" * 60)
    print(
        "LaTex found errors"
        "The final PDF won't be generated"
    )
    sys.exit(1)

# =========
#   PDF GENERATED
# =========

source_pdf = build_dir / "main.pdf"
if not source_pdf.exists():
    print()
    print(f"couldn't find generated pdf: {source_pdf}")
    sys.exit(1)


# ==========
#   Final pdf
# ===========

destination_pdf = actividad_dir / pdf_name

shutil.copy2(source_pdf, destination_pdf)

# ==========
#   Result
# ==========

print()
print("=" * 60)
print("PDF GENERATED OK")
print("=" * 60)

print()
print(f"Final document: {destination_pdf.relative_to(ROOT)}")

print()
print(f"Temporal documents: {build_dir.relative_to(ROOT)}")
print()


# ============
#   Open PDF for verification
# =============

# if sys.platform == "darwin":
#     subprocess.run(
#         [
#             "open",
#             str(destination_pdf)
#         ],
#         check=False
#     )