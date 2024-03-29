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

```
<TabHost android:id="@android:id/tabhost" android:layout_width="fill_parent" android:layout_height="fill_parent"
  xmlns:android="http://schemas.android.com/apk/res/android">
    <LinearLayout android:orientation="vertical" android:layout_width="fill_parent" android:layout_height="fill_parent">
        <TabWidget android:id="@android:id/tabs" android:background="#ff550000" android:layout_width="fill_parent" android:layout_height="wrap_content" android:divider="@drawable/tab_separator" />
        <FrameLayout android:id="@android:id/tabcontent" android:layout_width="fill_parent" android:layout_height="fill_parent">
            <TextView android:id="@id/last" android:layout_width="fill_parent" android:layout_height="fill_parent" android:text="Last" />
            <TextView android:id="@id/tags" android:layout_width="fill_parent" android:layout_height="fill_parent" android:text="Tags" />
        </FrameLayout>
    </LinearLayout>
</TabHost>
```

4) Fragments

Search for elements with the ```<fragment>``` tag

5) Horizontal paging

Find elements with the ViewPager ViewGroup element.

6) Action Bar with Tabs

7) Up Navigation

8) Navigation Drawers

Make sure that the root ViewGroup is DrawerLayout and it has 2 children.

## UI Features

Example UI layout screens that one can search for:

1) Example OAuth Login Screen
```
<RelativeLayout>
  <ImageView>
  <FrameLayout>
    <LinearLayout>
      <FrameLayout>
        <Button />
      </FrameLayout>
      <LinearLayout>
        <FrameLayout>
          <Button />
        </FrameLayout>
          <Button />
        <FrameLayout>
        </FrameLayout>
      </LinearLayout>
      <TextView />
    </LinearLayout>
  </FrameLayout>
</RelativeLayout>
```

![Sunrise Login](https://cloud.githubusercontent.com/assets/2602786/6072273/e0e2fc04-ad5c-11e4-9cda-c10f94d9fae3.png)

2) A Calendar screen

```
<View>
  <LinearLayout>
  </LinearLayout>
  <FrameLayout>
    <RelativeLayout>
      <LinearLayout>
        <FrameLayout>
          <LinearLayout>
            <LinearLayout>
              <TextView /><TextView /><TextView /><TextView /><TextView /><TextView /><TextView />
              <View />
            </LinearLayout>
            <ListView>
              <View /><View /><View /><View /><View /><View />
            </ListView>
          </LinearLayout>
        </FrameLayout>
      </LinearLayout>
    </RelativeLayout>
  </FrameLayout>
</View>
```
![Calendar](https://cloud.githubusercontent.com/assets/2602786/6072402/9a40fab0-ad5e-11e4-918b-45eef023a0c9.png)

3) Left-column tabular view with chat

```
<LinearLayout>
  <FrameLayout>
    <FrameLayout>
      <FrameLayout>
        <ImageView />
      </FrameLayout>
      <LinearLayout>
        <FrameLayout>
          <ImageView />
        </FrameLayout>
        <FrameLayout>
          <ImageView />
        </FrameLayout>
        <ListView>
          <RelativeLayout>
            <ImageView />
          </RelativeLayout>
        </ListView>
      </LinearLayout>
    </FrameLayout>
  </FrameLayout>
  <RelativeLayout>
    <FrameLayout>
      <FrameLayout>
        <LinearLayout>
          <FrameLayout>
            <LinearLayout>
              <MultiAutoCompleteTextView />
            </LinearLayout>
            <View />
          </FrameLayout>
          <ListView />
        </LinearLayout>
      </FrameLayout>
    </FrameLayout>
    <FrameLayout>
      <LinearLayout>
        <View />
        <LinearLayout>
          <ImageView />
          <EditText />
          <ImageView />
        </LinearLayout>
      </LinearLayout>
    </FrameLayout>
  </RelativeLayout>
</LinearLayout>
```

![Left Tabular Column](https://cloud.githubusercontent.com/assets/2602786/6072786/d75a6036-ad62-11e4-99ba-86e1e9f2e0f3.png)

4) Header Navigation

```
<FrameLayout>
  <FrameLayout>
    <FrameLayout>
      <ImageView />
    </FrameLayout>
  </FrameLayout>  
  
  <FrameLayout>
    <FrameLayout>
      <HorizontalScrollView>
        <LinearLayout>
          <TextView />
          <TextView />
          <TextView />
        </LinearLayout>
      </HorizontalScrollView>
    </FrameLayout>
  </FrameLayout>
</FrameLayout>
```

![Title bar](https://cloud.githubusercontent.com/assets/2602786/6156948/d5c9c724-b1fa-11e4-8832-7b7a8d61ebad.png)

5) Information Body

```
<LinearLayout>
  <LinearLayout>
    <LinearLayout>
      <LinearLayout>
        <View />
        <View />
        <View />
        <TextView />
      </LinearLayout>
    </LinearLayout>
  </LinearLayout>
</LinearLayout>
<LinearLayout>
  <LinearLayout>
    <LinearLayout>
      <ImageView />
      <LinearLayout>
        <TextView />
      </LinearLayout>
      <TextView />
    </LinearLayout>
  </LinearLayout>
  <FrameLayout>
    <FrameLayout>
      <FrameLayout>
        <FrameLayout>
          <RelativeLayout>
            <ImageView />
          </RelativeLayout>
          <View>
            <View />
          </View>
          <RelativeLayout />
        </FrameLayout>
      </FrameLayout>
    </FrameLayout>
  </FrameLayout>
</LinearLayout>
```

![Information Body](https://cloud.githubusercontent.com/assets/2602786/6218719/6c738d7c-b5de-11e4-8ca7-03ba304610ed.png)

6) Two-Column Tile View

```
<ListView>
  <LinearLayout>
    <FrameLayout>
      <ImageView />
      <TextView />
      <TextView />
    </FrameLayout>
    <FrameLayout>
      <ImageView />
      <TextView />
      <TextView />
    </FrameLayout>
  </LinearLayout>
</ListView>
```

![Two-Column Tile View](https://cloud.githubusercontent.com/assets/2602786/6218812/967ddbb2-b5df-11e4-84dd-f3e2b42e772b.png)

7) Timer Clock

```
<View>
  <View />
  <TextView />
  <Button />
  <ImageButton />
</View>
```

![Timer Clock](https://cloud.githubusercontent.com/assets/2602786/6219835/e60f948e-b5eb-11e4-9048-0130f95d13c3.png)

8) Information Cards

```
<FrameLayout>
  <LinearLayout>
    <LinearLayout>
      <FrameLayout>
        <ImageView />
        <LinearLayout>
          <TextView />
          <TextView />
        </LinearLayout>
      </FrameLayout>
    </LinearLayout>
    <FrameLayout>
      <View />
    </FrameLayout>
    <LinearLayout>
      <FrameLayout>
        <ImageView />
        <LinearLayout>
          <TextView />
          <TextView />
        </LinearLayout>
      </FrameLayout>
    </LinearLayout>
    <FrameLayout>
      <View />
    </FrameLayout>
    <RelativeLayout>
      <ImageView />
      <TextView />
    </RelativeLayout>
  </LinearLayout>
</FrameLayout>
```

![Timer Clock](https://cloud.githubusercontent.com/assets/2602786/6219923/e6a08de4-b5ec-11e4-8e17-87127844aa43.png)

9) Audio Cards

```
<LinearLayout>
  <FrameLayout>
    <RelativeLayout>
      <LinearLayout>
        <ImageView />
        <TextView />
      </LinearLayout>
      <TextView />
      <View />
      <ImageView />
      <View />
      <TextView />
      <TextView />
      <TextView />
      <TextView />
      <TextView />
      <TextView />
      <TextView />
      <FrameLayout>
        <TextView />
      </FrameLayout>
    </RelativeLayout>
  </FrameLayout>
</LinearLayout>
```

![Audio Cards](https://cloud.githubusercontent.com/assets/2602786/6220064/a4a3e92a-b5ee-11e4-990d-0f0e13b6055a.png)

10) Reminders Checklist

```
<EditText />
<LinearLayout>
  <ImageView />
  <CheckBox />
  <EditText />
</LinearLayout>
<LinearLayout>
  <ImageView />
  <CheckBox />
  <EditText />
</LinearLayout>
<LinearLayout>
  <ImageView />
  <CheckBox />
  <EditText />
</LinearLayout>
<LinearLayout>
  <LinearLayout>
    <ImageView />
    <EditText />
  </LinearLayout>
</LinearLayout>
```

![Reminders Checklist](https://cloud.githubusercontent.com/assets/2602786/6220148/cffaa5ae-b5ef-11e4-8641-0b379c1a8210.png)
