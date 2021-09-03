
def sanitize_name(name):
    """
    Function to sanitize names to docker safe image names
    TODO melhorar
    """
    return name.lower().replace(" ", "-")