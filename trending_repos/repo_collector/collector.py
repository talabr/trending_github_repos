import optparse
import os

import gtrending
from git import Repo, GitCommandError
from pip_check_reqs import common, find_extra_reqs
from prettytable import PrettyTable


class GitRepo(object):
    def __init__(self, repo_dict):
        self.repositoryName = repo_dict.get('name')
        self.author = repo_dict.get('author')
        self.avatar = repo_dict.get('avatar')
        self.description = repo_dict.get('description')
        self.url = repo_dict.get('url')
        self.language = repo_dict.get('language')
        self.stars = repo_dict.get('stars')
        self.forks = repo_dict.get('forks')
        self.built_by = [user.get('username') for user in repo_dict.get('builtBy')]
        self.security_score = None

    def set_security_score(self, score):
        if score is None:
            score = "Unknown"
        self.security_score = score

    def to_row(self):
        return [self.repositoryName, self.author, self.description, self.url, self.language, self.security_score]


class GitRepoCollector(object):
    def __init__(self, language):
        self.language = language
        self.repos = []

    def run(self, num_of_repos):
        print(f"Collecting top {num_of_repos} repositories from the most trending repos in Github")
        try:
            trending_repos = gtrending.fetch_repos(language=self.language)
            if 0 < num_of_repos < 25:
                trending_repos = trending_repos[:num_of_repos]
        except ValueError as e:
            print(f"Failed retrieving repos from Github. Error: {e}")
        else:
            for repo in trending_repos:
                git_repo_obj = GitRepo(repo)
                repo = self.clone_repo(git_repo_obj)
                if repo:
                    repo_path = os.path.abspath(git_repo_obj.repositoryName)
                    git_repo_obj.set_security_score(self.get_security_score(repo_path))
                    self.repos.append(git_repo_obj)
        self.pretty_print_repos()

    def clone_repo(self, git_repo_obj):
        repo = None
        name = git_repo_obj.repositoryName
        print(f"Looking for local copy of repo [{name}]...")
        if os.path.isdir(name):
            print(f"Found local copy. Using local")
            try:
                repo = Repo(name)
            except Exception as e:
                print(f"Failed using local repo. Error: {e}")
        else:
            print(f'No local copy. Cloning repo from Github...')
            try:
                repo = Repo.clone_from(git_repo_obj.url, name)
                print(f'Successfully cloned repo')
            except GitCommandError as e:
                print(f'Failed to clone repo. Error: {e}')
        return repo

    def get_security_score(self, repo_path):
        risk_score = 0
        options = self._build_options_and_args(repo_path)
        reqs_path = f"{repo_path}{os.path.sep}requirements.txt"
        if os.path.isfile(reqs_path):
            extra_reqs = find_extra_reqs.find_extra_reqs(options, reqs_path)
            risk_score = len(extra_reqs)
            print(f"Found {risk_score} unused packages in repo")
        else:
            print(f"Repo does not have a requirements.txt file. Unable to calculate risk score")
        return risk_score

    def _build_options_and_args(self, repo_path):
        usage = 'usage: %prog [options] files or directories'
        parser = optparse.OptionParser(usage)
        parser.add_option("--requirements-file",
                          dest="requirements_filename",
                          metavar="PATH",
                          default=f"{repo_path}\\requirements.txt",
                          help="path to the requirements file "
                               "(defaults to \"requirements.txt\")")
        parser.add_option("-n",
                          "--num_files",
                          type=int,
                          dest="num_files",
                          action="store",
                          default=25,
                          help="file paths globs to ignore")
        parser.add_option("-o",
                          "--os_type",
                          dest="os_type",
                          type=str,
                          action="store",
                          default='windows',
                          help="file paths globs to ignore")
        parser.add_option("-f",
                          "--ignore-file",
                          dest="ignore_files",
                          action="append",
                          default=[],
                          help="file paths globs to ignore")
        parser.add_option("-m",
                          "--ignore-module",
                          dest="ignore_mods",
                          action="append",
                          default=[],
                          help="used module names (globs are ok) to ignore")
        parser.add_option("-r",
                          "--ignore-requirement",
                          dest="ignore_reqs",
                          action="append",
                          default=[],
                          help="reqs in requirements to ignore")
        parser.add_option("-s",
                          "--skip-incompatible",
                          dest="skip_incompatible",
                          action="store_true",
                          default=False,
                          help="skip requirements that have incompatible "
                               "environment markers")
        parser.add_option("-v",
                          "--verbose",
                          dest="verbose",
                          action="store_true",
                          default=False,
                          help="be more verbose")
        parser.add_option("-d",
                          "--debug",
                          dest="debug",
                          action="store_true",
                          default=False,
                          help="be *really* verbose")
        parser.add_option("-V", "--version",
                          dest="version",
                          action="store_true",
                          default=False,
                          help="display version information")

        (options, args) = parser.parse_args()

        options.ignore_files = common.ignorer(options.ignore_files)
        options.ignore_mods = common.ignorer(options.ignore_mods)
        options.ignore_reqs = common.ignorer(options.ignore_reqs)

        options.paths = args
        return options

    def pretty_print_repos(self):
        x = PrettyTable()
        x.field_names = ['Repository Name', 'Author', 'Description', 'URL', 'Language', 'Security Score']
        x._max_width = {'Repository Name': 20, 'Author': 20, 'Description': 30, 'URL': 20, 'Language': 7, 'Security Score': 4}
        for repo_obj in self.repos:
            x.add_row(repo_obj.to_row())
        print(x)

