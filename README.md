# scrapy-kingston

Web crawler for Kingston ([kingston.com](https://kingston.com))

## Requirements

* Python
* [Scrapy](https://scrapy.org/)

## Notes

* 30 day cache is used in `settings.py`

## Spiders

All items are downloaded as JSON in the `items/` directory.

### Memory modules for certain manufacturer's all motherboards

For example all motherboard memory modules from Supermicro's motherboards:

    scrapy crawl manufacturer -a manufacturer="SMI"
    
This will generate `items/Memory/SMI/<motherboard model>.json` which then lists all compatible memory modules for this motherboard.
