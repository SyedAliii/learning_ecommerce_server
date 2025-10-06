import uuid
from slugify import slugify

def get_truncated_string(input_string: str, limit: int) -> str:
    if len(input_string) <= limit:
        return input_string
    return input_string[:limit]

def generate_unique_uuid():
    return str(uuid.uuid4())[:4]

def generate_product_slug(category: str, subcategory: str, title: str, id: str) -> str:
    truncate_limit = 6
    category_slug = slugify(category)
    category_slug = get_truncated_string(category_slug, truncate_limit)
    subcategory_slug = slugify(subcategory)
    subcategory_slug = get_truncated_string(subcategory_slug, truncate_limit)
    title_slug = slugify(title)
    title_slug = get_truncated_string(title_slug, truncate_limit)
    return f"{category_slug}/{subcategory_slug}/{title_slug}/{id}"