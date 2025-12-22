from dataclasses import dataclass
import argparse
from pathlib import Path

@dataclass
class Args:
    path: Path
    programmeringsolympiden: bool
    strict: bool

def get_argparser():
    parser = argparse.ArgumentParser(description='Stylecheck PO problems')
    parser.add_argument('directory', type=Path, help='Directory to recursively stylecheck')
    parser.add_argument('-s', '--strict', help='Apply strict checks', action='store_true')
    parser.add_argument('--PO', help='Apply Programmeringsolympiaden checks', action='store_true')
    return parser

def argparse_to_args(args):
    return Args(path=args.directory, programmeringsolympiden=args.PO, strict=args.strict)

def parse_only_path_args(path: Path):
    return argparse_to_args(get_argparser().parse_args([str(path)]))

def parse_cmdline_args():
    return argparse_to_args(get_argparser().parse_args())
