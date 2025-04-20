from src.config.settings import Settings
from src.utils.parse_args import parse_args

from src.core.controller import Controller

def main():
    args = parse_args()

    settings = Settings(
        seed_file=args.seeds,
        page_limit=args.limit,
        debug=args.debug
    )

    controller = Controller(settings)
    controller.run()

if __name__ == "__main__":
    main()