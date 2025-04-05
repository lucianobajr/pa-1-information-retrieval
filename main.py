from src.config.settings import Settings
from src.utils.parse_args import parse_args
from src.infra.frontier import get_seeds_from_file
from src.core.crawler_service import CrawlerService

def main():
    args = parse_args()

    settings = Settings(
        seed_file=args.seeds,
        page_limit=args.limit,
        debug=args.debug
    )

    crawler = CrawlerService(settings=settings)
    
    crawler.run()


if __name__ == "__main__":
    main()
