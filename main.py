#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from scrapy.cmdline import execute

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", "FCP"])
