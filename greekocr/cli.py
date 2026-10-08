"""Offline CLI; acquiring source data and deploying remain explicit Python APIs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Sequence
__all__ = ['main']

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='greekocr')
    parser.add_argument('--version', action='version', version='greekocr 0.1.0')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('recipes')
    verify = commands.add_parser('verify-recipe'); verify.add_argument('recipe'); verify.add_argument('--sha256')
    score = commands.add_parser('score'); score.add_argument('readings', type=Path)
    annotate = commands.add_parser('annotate'); annotate.add_argument('text')
    mix = commands.add_parser('validate-mix'); mix.add_argument('manifest', type=Path)
    mix.add_argument('--repo', type=Path, required=True); mix.add_argument('--role', default='train')
    env = commands.add_parser('env-plan'); env.add_argument('name'); env.add_argument('venv', type=Path)
    env.add_argument('--wheelhouse', type=Path); env.add_argument('--paddle-requirements', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'recipes':
            from greekocr.synth import recipe_registry
            result = {k:dict(path=str(v.path),sha256=v.sha256,origin_commit=v.origin_commit) for k,v in recipe_registry().items()}
        elif args.command == 'verify-recipe':
            from greekocr.synth import verify_recipe_sha
            result = dict(sha256=verify_recipe_sha(args.recipe, args.sha256))
        elif args.command == 'annotate':
            from greekocr.annotate import line_categories, word_tags, script_class
            result = dict(script_class=script_class(args.text), categories=line_categories(dict(text=args.text)), word_tags=word_tags(args.text))
        elif args.command == 'score':
            from greekocr.score import score_readings
            result = score_readings([json.loads(s) for s in args.readings.read_text().splitlines() if s.strip()])
        elif args.command == 'validate-mix':
            from greekocr.synth import validate_mix
            result = validate_mix(args.manifest, repo=args.repo, role=args.role)
        else:
            from greekocr.deploy.node_envs import environment_plan
            result = environment_plan(args.name,args.venv,wheelhouse=args.wheelhouse,paddle_requirements=args.paddle_requirements)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error),file=__import__('sys').stderr)
        return 3
