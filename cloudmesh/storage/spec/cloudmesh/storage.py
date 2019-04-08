#
# BUG
#

def get(storage, source, destinatiion, recursive):
    """Returns all users
  """

    from cloudmesh.storage.Provider import Provider

    provider = Provider(storage)

    result = provider.get(storage,
                          SOURCE,
                          DESTINATION,
                          recursive)

    return josonify(result)
