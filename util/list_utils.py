def deduplicate_documents(document_list):
    unique_documents = {}
    for item in document_list:
        document = item["Document"]
        if document not in unique_documents:
            unique_documents[document] = item
    return list(unique_documents.values())


def deduplicate_nested_list(nested_list):
    # Convert each item to a string representation
    string_list = [str(item) for sublist in nested_list for item in sublist]

    # Create a set from the string representations to remove duplicates
    unique_string_list = set(string_list)

    # Convert the unique strings back to the original type
    item_type = type(nested_list[0][0])
    unique_items = [parse_personal_info(item, item_type) for item in unique_string_list]

    # Convert the unique items back to the original structure
    unique_nested_list = [unique_items[i:i + len(nested_list[0])] for i in
                          range(0, len(unique_items), len(nested_list[0]))]

    return type(nested_list)(unique_nested_list)


def parse_personal_info(string_repr, item_type):
    attributes = {}
    for attribute in string_repr.split():
        if '=' in attribute:
            key, value = attribute.split('=')
            attributes[key.strip()] = parse_value(value.strip())
    return item_type(**attributes)


def parse_value(value):
    if value == 'None':
        return None
    elif value.isdigit():
        return int(value)
    return value.strip('\'\"')
