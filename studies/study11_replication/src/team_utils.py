"""Shared helper: parse team from a meeting id, consistent with every prior study in this program."""
import re

def team_of(mid):
    return "startup_a" if "startup_a" in mid else "startup_b"

TEAMS = ["startup_a", "startup_b"]
NICE = {"startup_a": "Team A", "startup_b": "Team B"}
