from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys, json
from datetime import datetime, timedelta

import boto3, requests

from . import register_parser
from .util import paginate, Timestamp
from .util.printing import format_table, page_output, tabulate, format_datetime
from .util.aws import region_name, offers_api, clients, instance_type_completer, get_products
from .util.compat import median

def pricing(args):
    if args.spot:
        args.columns = args.columns_spot
        paginator = clients.ec2.get_paginator("describe_spot_price_history")
        page_output(tabulate(paginate(paginator, StartTime=args.spot_start_time), args))
    elif args.service_code:
        if args.region is None:
            args.region = clients.ec2.meta.region_name
        args.columns += getattr(args, "columns_" + args.service_code, [])
        args.filters += getattr(args, "filters_" + args.service_code, [])
        if hasattr(args, "sort_by_" + args.service_code):
            args.sort_by = getattr(args, "sort_by_" + args.service_code)
        filters = [("location", region_name(args.region))] + args.filters
        table = get_products(args.service_code, region=args.region, filters=filters, terms=args.terms,
                             max_cache_age_days=args.max_cache_age_days)
        page_output(tabulate(table, args))
    else:
        client = boto3.client("pricing", region_name="us-east-1")
        args.columns = ["ServiceCode", "AttributeNames"]
        page_output(tabulate(paginate(client.get_paginator("describe_services")), args))

parser = register_parser(pricing, help="List AWS prices")
parser.add_argument("service_code", nargs="?", help="""
AWS product offer to list prices for. Run without this argument to see the list of available product service codes.""")
parser.add_argument("--columns", nargs="+")
parser.add_argument("--filters", nargs="+", metavar="NAME=VALUE", type=lambda x: x.split("=", 1), default=[])
parser.add_argument("--terms", nargs="+", default=["OnDemand"])
parser.add_argument("--sort-by")
parser.add_argument("--spot", action="store_true", help="Display AWS EC2 Spot Instance pricing history")
parser.add_argument("--spot-start-time", type=Timestamp, default=Timestamp("-1h"), metavar="START",
                    help="Time to start spot price history." + Timestamp.__doc__)
parser.add_argument("-columns-spot")
