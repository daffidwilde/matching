import os
from glob import iglob


def main():
    """ Make all images in current directory. """

    for tex_file in iglob("./*.tex"):
        jobname = tex_file.split("/")[-1][:-4]
        os.system(f"pdflatex --shell-escape {jobname}")

        for ext in ["aux", "log", "pdf"]:
            os.system(f"rm {jobname}.{ext}")


if __name__ == "__main__":
    main()
