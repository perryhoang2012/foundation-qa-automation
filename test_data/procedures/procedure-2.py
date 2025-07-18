config = {
    "steps": [
        {
            "type": "get_all_mesh",
        },
        {
            "type": "get_all_system"
        },
        {
            "type": "get_all_source"
        },
        {
            "type": "get_all_object"
        },
        {
            "type": "get_object_by_id", 
            "ref": "object-abc"
        },
        {
            "type": "get_all_product"
        },
        {
            "type": "get_product_by_id", 
            "ref": "product-abc"
        },
    ],
}
