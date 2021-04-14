{
    "variables": [
        {
            "name": "gtin",
            "value": "gtin",
            "source": "other_data"
        },
        {
            "name": "channel",
            "value": "channel",
            "source": "other_data"
        },
        {
            "name": "internalRemarks",
            "value": "internalRemarks",
            "source": "other_data"
        },
        {
            "name": "polled_date",
            "value": "polled_date",
            "source": "other_data"
        },
        {
            "name": "source",
            "value": "source",
            "source": "other_data"
        },
        {
            "name": "description",
            "value": "$.data.GeneralInfo.SummaryDescription.LongSummaryDescription",
            "source": "json"
        },
        {
            "name": "short_description",
            "value": "$.data.GeneralInfo.SummaryDescription.ShortSummaryDescription",
            "source": "json"
        },
        {
            "name": "article_title",
            "value": "$.data.GeneralInfo.Title",
            "source": "json"
        }
    ],
    "fields": [
        {
            "reference": "",
            "destination": "$.articles.[0].gtin",
            "source": "gtin",
            "conditions": {
                "pattern": "0-9",
                "maxLength": "13",
                "minLength": "13"
            },
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].channel",
            "source": "channel",
            "conditions": {
                "pattern": "a-zA-Z0-9_",
                "maxLength": "50",
                "minLength": "3"
            },
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.attributeGenericInternalRemarks",
            "source": "internalRemarks",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.additionalProperties",
            "source": "additionalProperties",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].lifecycle.contentEnrichment.[0].ts",
            "source": "polled_date",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].lifecycle.contentEnrichment.[0].source",
            "source": "source",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.attributeGenericArticleDescription",
            "source": "description",
            "conditions": {
                "pattern": "-\"A-Za-zÀ-ßéèêěëėäàáâæãåāöôòóõœøōüûùúūůščřžýíÉÈÊĚËĖÄÀÁÂÆÃÅĀÖÔÒÓÕŒØŌÜÛÙÚŪŠČŘŽÝÍŮ0-9 _.,;'‘’“”&()=´®™:°%!<>/+",
                "maxLength": "5000",
                "minLength": "5"
            },
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.attributeGenericArticleTitle",
            "source": "article_title",
            "conditions": {
                "pattern": "-\"A-Za-zÀ-ßéèêěëėäàáâæãåāöôòóõœøōüûùúūůščřžýíÉÈÊĚËĖÄÀÁÂÆÃÅĀÖÔÒÓÕŒØŌÜÛÙÚŪŠČŘŽÝÍŮ0-9 _.,;'‘’“”&()=´®™:°%<>/+",
                "maxLength": "250",
                "minLength": "5"
            },
            "keyIndex": ""
        }
    ],
    "channel": "gkkCilIcecat",
    "statusCode": {
        "code": 200,
        "message": ""
    }
}