## Listing Details

Examples

1. Finds an addition of the word 'cool' in the title for all apps and all versions
```
{
  app: '*',
  version: '*',
  features: {'title': +'cool'}
}
```

2. Finds an increase in words in the description for all apps and all versions
```
{
  app: '*',
  version: '*',
  features: {'description': +'{words}'}
}
```

3. Finds a change in category from 'health' to 'productivity' for all apps and all versions
```
{
  app: '*',
  version: '*',
  features: {'category': {from: 'health', to: 'productivity'}}
}
```

4. Finds an $2.00 increase in price in all sports apps
```
{
  app: '*',
  version: '*',
  features: {'category': 'sports', 'price': +'2.00'}
}
```

5. Grabs all of the permissions for the first and third versions of Evernote
```
{
  app: 'com.evernote',
  version: '1, 3',
  features: {'permissions'}
}
```

6. Retrieves all listing features for the first version of Evernote
```
{
  app: 'com.evernote',
  version: '3',
  features: {}
}
```
