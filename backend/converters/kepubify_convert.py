import os
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Optional

from core import validate_safe_path

from .converter_interface import ConverterInterface


class KepubifyConverter(ConverterInterface):
    """Convert EPUB ebooks to Kobo's KEPUB format using the ``kepubify`` CLI.

    Kobo eReaders natively render EPUB but use an extended Kobo-flavored EPUB
    (KEPUB) for features like accurate progress tracking and faster page
    turns. ``kepubify`` is a standalone Go tool that produces those files
    significantly faster than Calibre's KEPUB plugin.
    """

    supported_input_formats = {'epub'}
    supported_output_formats = {'kepub'}

    kepubify_paths = {
        'darwin': '/opt/homebrew/bin/kepubify',
        'linux': '/usr/local/bin/kepubify',
        'win32': 'C:\\Program Files\\kepubify\\kepubify.exe',
    }
    kepubify_path = kepubify_paths.get(sys.platform, 'kepubify')

    def __init__(self, input_file: str, output_dir: str, input_type: str, output_type: str):
        super().__init__(input_file, output_dir, input_type, output_type)

    @classmethod
    def can_register(cls) -> bool:
        """Return True when the ``kepubify`` binary is available on PATH."""
        try:
            # Subprocess is safe here because the command is constructed without
            # user input.
            subprocess.run(  # nosec B603 B607
                [cls.kepubify_path, '--version'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def can_convert(self) -> bool:
        return (
            self.input_type.lower() in self.supported_input_formats
            and self.output_type.lower() in self.supported_output_formats
        )

    def convert(self, overwrite: bool = True, quality: Optional[str] = None) -> list[str]:
        """Convert the EPUB to KEPUB using ``kepubify``.

        ``kepubify``'s default output extension is ``.kepub.epub``; we mirror
        that here so downstream filename handling stays consistent with the
        Kobo ecosystem.
        """
        if not self.can_convert():
            raise ValueError(
                f"Conversion from {self.input_type} to {self.output_type} is not supported."
            )

        if not os.path.isfile(self.input_file):
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        input_stem = Path(self.input_file).stem
        output_file = os.path.join(self.output_dir, f"{input_stem}.kepub.epub")

        if not overwrite and os.path.exists(output_file):
            return [output_file]

        # If overwriting, remove any pre-existing artifact so kepubify treats
        # the path as a target filename rather than a directory.
        if overwrite and os.path.exists(output_file):
            os.remove(output_file)

        validate_safe_path(self.input_file)
        validate_safe_path(output_file)

        cmd = [
            self.kepubify_path,
            '--output', output_file,
            self.input_file,
        ]

        try:
            # Subprocess is safe here because the input file path is validated
            # and the command is constructed without user input.
            result = subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"kepubify conversion failed: {e.stderr or e.stdout or str(e)}"
            )
        except Exception as e:
            raise RuntimeError(f"kepubify conversion failed: {str(e)}")

        if not os.path.exists(output_file):
            raise RuntimeError(
                f"Output file was not created: {output_file}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Stdout: {result.stdout}\n"
                f"Stderr: {result.stderr}"
            )

        return [output_file]
