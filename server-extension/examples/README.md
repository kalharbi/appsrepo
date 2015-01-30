## Listing Details

Examples

1) Finds an addition of the word 'cool' in the title for all apps and all versions
```
{
  app: '*',
  version: '*',
  features: {'title': +'cool'}
}
```

2) Finds an increase in words in the description for all apps and all versions
```
{
  app: '*',
  version: '*',
  features: {'description': +'{words}'}
}
```

3) Finds a change in category from 'health' to 'productivity' for all apps and all versions

```
{
  app: '*',
  version: '*',
  features: {'category': {from: 'health', to: 'productivity'}}
}
```

4) Finds an $2.00 increase in price in all sports apps
```
{
  app: '*',
  version: '*',
  features: {'category': 'sports', 'price': +'2.00'}
}
```

5) Grabs all of the permissions for the first and third versions of Evernote
```
{
  app: 'com.evernote',
  version: '1, 3',
  features: {'permissions'}
}
```

6) Retrieves all listing features for the first version of Evernote
```
{
  app: 'com.evernote',
  version: '3',
  features: {}
}
```

## Layout Features

Examples

1) Custom UI widgets
Custom UI widgets are named after the package name.

```
<com.android.notepad.MyEditText
  id="@+id/note"
  ... />
```

2) Resizeable Homescreen widgets
In the AndroidManifest.xml file, there is a receiver tag.

```
<receiver android:name="ExampleAppWidgetProvider" >
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data android:name="android.appwidget.provider"
               android:resource="@xml/example_appwidget_info" />
</receiver>
```

In the android:resources file, look for the ```<appwidget-provider>``` tag with a resizeMode attribute

```
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="40dp"
    android:minHeight="40dp"
    android:updatePeriodMillis="86400000"
    android:previewImage="@drawable/preview"
    android:initialLayout="@layout/example_appwidget"
    android:configure="com.example.android.ExampleAppWidgetConfigure" 
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen|keyguard"
    android:initialKeyguardLayout="@layout/example_keyguard">
</appwidget-provider>
```

3) Tab layouts with TabHost
Find a ViewGroup element named TabHost with a view element named TabWidget.

4) Fragments

5) Horizontal paging

6) Action Bar with Tabs

7) Up Navigation

8) Navigation Drawers
