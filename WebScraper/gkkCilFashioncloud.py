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
            "value": "$.data.[0].manufacturerAttributes.description",
            "source": "json"
        },
        {
            "name": "short_description",
            "value": "$.data.[0].manufacturerAttributes.shortDescription",
            "source": "json"
        },
        {
            "name": "brand",
            "value": "brand",
            "source": "other_data"
        },
        {
            "name": "styleGroupId",
            "value": "$.data.[0].styleGroupId",
            "source": "json"
        },
        {
            "name": "category",
            "checkValue": [
                "$.data[0].fcKeys.category",
                "$.data[0].fcAttributes.category",
                "$.data[0].manufacturerAttributes.category"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "article_title",
            "checkValue": [
                "$.data[0].fcKeys.name",
                "$.data[0].fcAttributes.name",
                "$.data[0].manufacturerAttributes.name"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "fit",
            "value": "$.data[0].manufacturerAttributes.fit",
            "source": "json"
        },
        {
            "name": "target_group",
            "checkValue": [
                "$.data[0].fcKeys.targetGroup",
                "$.data[0].fcAttributes.targetGroup",
                "$.data[0].manufacturerAttributes.targetGroup"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "heel_height",
            "value": "$.data[0].manufacturerAttributes.heelHeight",
            "source": "json"
        },
        {
            "name": "heel_type",
            "value": "$.data[0].manufacturerAttributes.heelType",
            "source": "json"
        },
        {
            "name": "season",
            "checkValue": [
                "$.data[0].fcKeys.season",
                "$.data[0].fcAttributes.season",
                "$.data[0].manufacturerAttributes.season"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "size_fashion",
            "checkValue": [
                "$.data[0].fcKeys.size",
                "$.data[0].fcAttributes.size",
                "$.data[0].manufacturerAttributes.size"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "raw_material",
            "checkValue": [
                "$.data[0].fcKeys.materials",
                "$.data[0].fcAttributes.materials",
                "$.data[0].manufacturerAttributes.materials"
            ],
            "source": "json",
            "value": ""
        },
        {
            "name": "search_color",
            "checkValue": [
                "$.data[0].fcKeys.searchColors[0]",
                "$.data[0].fcAttributes.searchColors[0]",
                "$.data[0].manufacturerAttributes.searchColors[0]"
            ],
            "source": "json",
            "value": "",
            "convertTypeTo": "array"
        },
        {
            "name": "care_label",
            "checkValue": [
                "$.data[0].fcKeys.careInstruction",
                "$.data[0].fcAttributes.careInstruction",
                "$.data[0].manufacturerAttributes.careInstruction"
            ],
            "source": "json",
            "value": ""
        },
        {
            "reference": "FC_CAREFASHION",
            "name": "care_label_text",
            "source": "variable",
            "value": "care_label",
            "convertTypeTo": "str"
        },
        {
            "name": "fc_care_label",
            "value": "$.data[0].fcKeys.careInstruction",
            "source": "json"
        },
        {
            "valueStartsWith": "1_",
            "name": "fc_care_label_washing",
            "source": "variable",
            "value": "fc_care_label"
        },
        {
            "valueStartsWith": "2_",
            "name": "fc_care_label_bleaching",
            "source": "variable",
            "value": "fc_care_label"
        },
        {
            "valueStartsWith": "3_",
            "name": "fc_care_label_drying",
            "source": "variable",
            "value": "fc_care_label"
        },
        {
            "valueStartsWith": "4_",
            "name": "fc_care_label_ironing",
            "source": "variable",
            "value": "fc_care_label"
        },
        {
            "valueStartsWith": "5_",
            "name": "fc_care_label_dry_cleaning",
            "source": "variable",
            "value": "fc_care_label"
        },
        {
            "name": "raw_materials",
            "value": "$.data[0].fcKeys.materials[0].composition",
            "source": "json"
        },
        {
            "name": "material",
            "checkValue": [
                "$.data[0].fcKeys.material",
                "$.data[0].fcAttributes.material",
                "$.data[0].manufacturerAttributes.material"
            ],
            "source": "json",
            "value": ""
        }
    ],
    "fields": [
        {
            "destination": "$.articles.[0].gtin",
            "source": "gtin"
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
            "reference": "PL_BRAND",
            "destination": "$.articles.[0].articleAttributes.brand",
            "source": "brand",
            "conditions": {},
            "allowMagicMatch": true,
            "keyIndex": ""
        },
        {
            "destination": "$.articles.[0].references.dataSupplier.sourceParentRef",
            "source": "styleGroupId"
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
                "pattern": "-\"A-Za-zÀ-ßéèêěëėäàáâæãåāöôòóõœøōüûùúūůščřžýíÉÈÊĚËĖÄÀÁÂÆÃÅĀÖÔÒÓÕŒØŌÜÛÙÚŪŠČŘŽÝÍŮ0-9 _.,;'‘’“”&()=´®™:°%<>/+",
                "maxLength": "5000",
                "minLength": "5"
            },
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.descriptionShort",
            "source": "short_description",
            "conditions": {
                "pattern": "-\"A-Za-zÀ-ßéèêěëėäàáâæãåāöôòóõœøōüûùúūůščřžýíÉÈÊĚËĖÄÀÁÂÆÃÅĀÖÔÒÓÕŒØŌÜÛÙÚŪŠČŘŽÝÍŮ0-9 _.,;'‘’“”&()=´®™:°%<>/+",
                "maxLength": "2000",
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
        },
        {
            "reference": "FC_CLASSIFICATION",
            "destination": "$.articles.[0].classification.main",
            "source": "category",
            "conditions": {
                "maxLength": "200",
                "minLength": "5"
            },
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.attributeGenericManufacturerSize",
            "source": "size_fashion",
            "conditions": {
                "pattern": "A-Za-zÀ-ž0-9 _.,&()=´®™:°%<>/+-",
                "maxLength": "50",
                "minLength": "1"
            },
            "keyIndex": ""
        },
        {
            "reference": "FC_SEASON",
            "destination": "$.articles.[0].articleAttributes.attributeGenericSeason",
            "source": "season",
            "conditions": {},
            "convertTypeTo": "array",
            "keyIndex": ""
        },
        {
            "reference": "FC_COLOR",
            "destination": "$.articles.[0].articleAttributes.attributeGenericManufacturerColor",
            "source": "search_color",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "FC_HEELSHAPE",
            "destination": "$.articles.[0].articleAttributes.attributeGenericHeelShape",
            "source": "heel_type",
            "allowMagicMatch": true,
            "keyIndex": ""
        },
        {
            "reference": "",
            "destination": "$.articles.[0].articleAttributes.attributeGenericMeasurements.measurementsNonStructured.[*]",
            "source": "heel_height",
            "conditions": {
                "pattern": "A-Za-zÀ-ž0-9 _.,&()=´®™:°%<>/+-",
                "maxLength": "500",
                "minLength": "3"
            },
            "keyIndex": ""
        },
        {
            "reference": "FC_TARGETGROUP",
            "destination": "$.articles.[0].articleAttributes.attributeGenericTargetGroup.generalTargetGroup",
            "source": "target_group",
            "conditions": {
                "pattern": "A-Za-zÀ-ž0-9 _.,&()=´®™:°%<>/+-",
                "maxLength": "30",
                "minLength": "3"
            },
            "keyIndex": ""
        },
        {
            "reference": "FC_FIT",
            "destination": "$.articles.[0].articleAttributes.fit",
            "source": "fit",
            "conditions": {},
            "keyIndex": ""
        },
        {
            "reference": "FC_CAREFASHION",
            "destination": "$.articles.[0].articleAttributes.attributeGenericCareLabelTextile.washing",
            "source": "fc_care_label_washing",
            "conditions": {},
            "keyIndex": "0"
        },
        {
            "reference": "FC_CAREFASHION",
            "destination": "$.articles.[0].articleAttributes.attributeGenericCareLabelTextile.bleaching",
            "source": "fc_care_label_bleaching",
            "conditions": {},
            "keyIndex": "0"
        },
        {
            "reference": "FC_CAREFASHION",
            "destination": "$.articles.[0].articleAttributes.attributeGenericCareLabelTextile.drying",
            "source": "fc_care_label_drying",
            "conditions": {},
            "keyIndex": "0"
        },
        {
            "reference": "FC_CAREFASHION",
            "destination": "$.articles.[0].articleAttributes.attributeGenericCareLabelTextile.ironing",
            "source": "fc_care_label_ironing",
            "conditions": {},
            "keyIndex": "0"
        },
        {
            "reference": "FC_CAREFASHION",
            "destination": "$.articles.[0].articleAttributes.attributeGenericCareLabelTextile.dryCleaning",
            "source": "fc_care_label_dry_cleaning",
            "conditions": {},
            "keyIndex": "0"
        },
        {
            "reference": "FC_FITUPPERPART",
            "destination": "$.articles.[0].articleAttributes.attributeGenericFitUpperPartsSkirtsAndDressesClothing",
            "source": "fit",
            "conditions": {
                "referenceData": {
                    "referenceVariable": "category",
                    "referenceTable": "FC_CATEGORYUPPER"
                }
            },
            "keyIndex": ""
        },
        {
            "reference": "FC_FITLOWERPART",
            "destination": "$.articles.[0].articleAttributes.attributeGenericFitLowerPartsClothing",
            "source": "fit",
            "conditions": {
                "referenceData": {
                    "referenceVariable": "category",
                    "referenceTable": "FC_CATEGORYLOWER"
                }
            },
            "keyIndex": ""
        },
        {
            "source": "raw_material",
            "group": [
                {
                    "reference": "FC_MATERIAL",
                    "source": "self",
                    "keyDestination": "$.articles.[0].articleAttributes.attributeGenericMaterialFashion.materialCompositionPerLocation.[0].locationPartsMaterial.[*].material",
                    "value": "$.composition.[0].material"
                },
                {
                    "source": "self",
                    "keyDestination": "$.articles.[0].articleAttributes.attributeGenericMaterialFashion.materialCompositionPerLocation.[0].locationPartsMaterial.[*].parts",
                    "value": "$.composition.[0].percentage",
                    "convertTypeTo": "int"
                },
                {
                    "reference": "FC_LOCATION",
                    "source": "self",
                    "keyDestination": "$.articles.[0].articleAttributes.attributeGenericMaterialFashion.materialCompositionPerLocation.[0].location",
                    "value": "$.partName"
                }
            ]
        }
    ],
    "channel": "gkkCilFashioncloud",
    "statusCode": {
        "code": 200,
        "message": ""
    }
}