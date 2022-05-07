import argparse
from trending_repos.repo_collector.collector import GitRepoCollector
SUPPORTED_LANGUAGE = "python"


def parse_args():
    parser = argparse.ArgumentParser(description=f'Tal CLI tool to present top n trending repositories from Github.'
                                                 f'**Currently supporting only Python**',
                                     usage='<> -n <num_of_trending_repos>')
    parser.add_argument('-n', '--num_of_trending', type=int, action='store', dest='num_of_trending',
                        help='Enter the number of trending Github repos to list. Number must be between 1-25.',
                        required=True, default=25)

    return parser.parse_args()


def run():
    try:
        args = parse_args()
    except Exception as e:
        print(f'Error while parsing arguments - {e}')
    else:
        num_of_trending_repos = args.num_of_trending if 0 < args.num_of_trending <= 25 else 25
        git_repo_collector = GitRepoCollector(language=SUPPORTED_LANGUAGE)
        git_repo_collector.run(num_of_trending_repos)


