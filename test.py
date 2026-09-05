<<<<<<< HEAD
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from agent import _tool_build_bundle, _tool_search_catalog


def main():
    search = _tool_search_catalog("trekking poles under 1500")
    assert search["matches"], "Expected at least one search result"
    assert all(p["price"] <= 1500 for p in search["matches"]), "Price filter failed"

    bundle = _tool_build_bundle("weekend trekking", 4000)
    assert bundle["success"], "Expected a bundle to fit"
    assert len(bundle["items"]) >= 2, "Growth bundle should contain complementary items"
    assert bundle["bundle_total"] <= 4000, "Bundle exceeded buyer budget"
    assert len({item["category"] for item in bundle["items"]}) == len(bundle["items"]), "Bundle should diversify categories"

    print("ProtoBuy regression tests: PASS")


if __name__ == "__main__":
    main()
=======
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from agent import _tool_build_bundle, _tool_search_catalog

def main():
    search=_tool_search_catalog('trekking poles under 1500')
    assert search['matches'] and all(p['price']<=1500 for p in search['matches'])
    bundle=_tool_build_bundle('weekend trekking',4000)
    assert bundle['success'] and len(bundle['items'])>=2 and bundle['bundle_total']<=4000
    assert len({item['category'] for item in bundle['items']})==len(bundle['items'])
    print('ProtoBuy regression tests: PASS')
if __name__=='__main__': main()
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
