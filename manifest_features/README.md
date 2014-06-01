## Manifest Features Collection
Store apps' AndroidManifest.xml features in a Mongodb collection named manifest.

### Requirements
* Required:
  * Python  2.7 or later.
  * [PyMongo 2.7.1]('http://api.mongodb.org/python/current/')
  * [PyYAML 3.11]('http://pyyaml.org/wiki/PyYAML')
* You can install the required packages using: ```pip install -r requirements.txt```

### Usage:
```
Usage: python manifest_features.py [options] apk_dir
The manifest_features tool recursively searches for a directory of unpacked
apk files, parses their AndroidManifest.xml files and stores them in a MongoDB 
collection named manifest.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l FILE, --log=FILE   write logs to FILE.
  -v, --verbose         Increase verbosity.
  -d DEPTH_VALUE, --depth=DEPTH_VALUE
                        The depth of the subdirectories to scan for
                        AndroidManifest.xml files.

```
##Manifest Features Collection
This is an example of running the query: 
```db.manifest.find({'package': 'com.evernote'}).pretty()```

```
{
	"_id" : ObjectId("536e47d4783678aea842311a"),
	"activities" : [
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.HomeActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.phone.PhoneMainActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.tablet.TabletMainActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/TransparentActivity.Dim.NoAnimation",
				"name" : "com.evernote.ui.ShortcutsActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.EvernoteMapActivity",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.SnippetActivity",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.maps.NoteListActivity",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.MapActivityGroup",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"configChanges" : "orientation|screenSize",
				"name" : "com.evernote.ui.maps.PinDropActivity",
				"launchMode" : "singleTop",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.amazon.EvernoteMapActivity",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.amazon.MapActivityGroup",
				"launchMode" : "singleTask",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.maps.amazon.PinDropActivity",
				"launchMode" : "singleTop",
				"label" : "@string/app_name"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.PinLockActivity"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.ui.SecurityPreferenceActivity",
				"launchMode" : "singleTask",
				"label" : "@string/pinllock_setting_title"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.phone.SwipeableNoteListActivity"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"name" : "com.evernote.ui.phone.SwipeableNoteListAloneActivity",
				"launchMode" : "singleTop",
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.EvernoteNotePickerActivity",
				"launchMode" : "singleTop"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.phone.SwipeableNoteViewActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.phone.HoneycombSwipeableNoteViewActivity"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"name" : "com.evernote.ui.phone.SwipeableNoteViewAloneActivity",
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.InformationActivity",
				"label" : "@string/notice"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.tablet.NoteListActivity"
			}
		},
		{
			"metaData" : [
				{
					"resource" : "@xml/searchable",
					"name" : "android.app.searchable"
				}
			],
			"activity" : {
				"allowTaskReparenting" : "true",
				"name" : "com.evernote.ui.GoogleSearchResultRedirectActivity",
				"launchMode" : "singleTop",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"name" : "com.evernote.ui.tablet.NoteListAloneActivity",
				"launchMode" : "singleTop",
				"theme" : "@style/PopUpActivity",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.tablet.NoteViewActivity"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"name" : "com.evernote.ui.tablet.NoteViewAloneActivity",
				"theme" : "@style/TransparentActivity.Dim",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.AccountInfoPreferenceActivity",
				"label" : "@string/evernote_settings"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.EvernotePreferenceActivity",
				"label" : "@string/evernote_settings"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"theme" : "@style/PopUpActivity",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.note.composer.NewNoteActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.ui.SkitchImageActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.note.composer.NewNoteAloneActivity",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"name" : "com.evernote.ui.WidgetNewNoteActivity",
				"label" : "@string/widget",
				"theme" : "@style/TranslucentPopUpActivity.Dim",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.newNoteTask"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TranslucentPopUpActivity.Dim",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.EmailActivity"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/FragmentDialogActivity",
				"name" : "com.evernote.ui.TagEditActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.NoteInfoActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.SkitchUpsellActivity"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.note.composer.FilePickerActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.AuthenticationActivity"
			}
		},
		{
			"activity" : {
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.WebActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.TrunkActivity"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"alwaysRetainTaskState" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/TranslucentPopUpActivity.Dim",
				"name" : "com.evernote.ui.SearchActivity"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"windowSoftInputMode" : "stateHidden",
				"name" : "com.evernote.ui.WidgetSearchActivity",
				"clearTaskOnLaunch" : "true",
				"theme" : "@style/TransparentPopUpActivity",
				"excludeFromRecents" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"taskAffinity" : "com.evernote.searchTask"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/PopUpActivity",
				"name" : "com.evernote.ui.AdvanceSearchActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.AdvanceSearchSelector"
			}
		},
		{
			"activity" : {
				"theme" : "@style/LandingScreen",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.landing.LandingActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Dialog",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.RateAppActivity",
				"label" : "@string/rate_app_title"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Dialog",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.DYNDialogActivity",
				"label" : "@string/dyn_title"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Dialog.Alert",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.StandardDialogActivity",
				"launchMode" : "singleTop"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Dialog",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.ShareWithFacebook",
				"label" : "@string/dyn_title"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Dialog.Alert",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.ShareDialogActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Dialog.Alert",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.SDCardChangedActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"allowTaskReparenting" : "true",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.ui.helper.URIBrokerActivity",
				"taskAffinity" : "com.evernote.standAlone"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"name" : "com.evernote.billing.AmazonBillingActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.billing.BillingActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity",
				"name" : "com.evernote.billing.BillingHelper$BillingHelperActivity",
				"launchMode" : "singleTask"
			}
		},
		{
			"activity" : {
				"theme" : "@style/TransparentActivity.Dim",
				"name" : "com.evernote.billing.LaunchBillingActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.smartnotebook.SmartNotebookSettingsActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.NotebookShareSettingsActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.NoteShareSettingsActivity"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/Theme.Light.NoTitle",
				"name" : "com.evernote.ui.EmailPickerActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/PopUpActivity",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.support.CustomerSupportActivity",
				"label" : "@string/cs_title"
			}
		},
		{
			"activity" : {
				"name" : "com.evernote.help.FeatureDiscoveryWidgetGet",
				"theme" : "@style/Theme.NewDialog.Transparent",
				"noHistory" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"excludeFromRecents" : "true",
				"taskAffinity" : "com.evernote.fullscreenfeatureDialog"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NewDialog.Transparent",
				"configChanges" : "keyboardHidden|screenSize",
				"name" : "com.evernote.help.FeatureDiscoveryPromo"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Light.NoTitle",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.help.PromoWebActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Light.NoTitle",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.BusinessLibraryActivity"
			}
		},
		{
			"activity" : {
				"name" : "com.evernote.help.FeatureDiscoveryWidgetConfig",
				"theme" : "@style/Theme.NewDialog.Transparent",
				"noHistory" : "true",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"excludeFromRecents" : "true",
				"taskAffinity" : "com.evernote.fullscreenfeatureDialog"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Light.Fullscreen",
				"screenOrientation" : "portrait",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.VideoCaptureActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Welcome",
				"name" : "com.evernote.ui.WelcomeActivity"
			}
		},
		{
			"activity" : {
				"windowSoftInputMode" : "stateHidden",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"theme" : "@style/Theme.NoTitle",
				"name" : "com.evernote.ui.UserSetupActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.NoTitle",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.ui.gallery.GalleryActivity"
			}
		},
		{
			"activity" : {
				"theme" : "@style/Theme.Light.NoTitle",
				"screenOrientation" : "portrait",
				"configChanges" : "keyboardHidden|orientation|screenSize",
				"name" : "com.evernote.smart.noteworthy.EventsActivity"
			}
		},
		{
			"activity" : {
				"process" : ":camera",
				"theme" : "@*android:style/Theme.NoTitleBar.Fullscreen",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.android.multishotcamera.MultiShotCameraActivity",
				"label" : "@string/amsc_app_name"
			}
		},
		{
			"activity" : {
				"process" : ":camera",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.android.multishotcamera.FilePickerActivity",
				"label" : "@string/amsc_app_name"
			}
		},
		{
			"activity" : {
				"process" : ":camera",
				"theme" : "@*android:style/Theme.NoTitleBar",
				"configChanges" : "keyboardHidden|orientation|screenLayout|screenSize",
				"name" : "com.evernote.android.multishotcamera.ViewImagesActivity",
				"label" : "View Images"
			}
		}
	],
	"providers" : [
		{
			"path_permission" : [
				{
					"pathPrefix" : "/search_suggest_query",
					"readPermission" : "android.permission.GLOBAL_SEARCH"
				}
			],
			"provider" : {
				"authorities" : "com.evernote.evernoteprovider",
				"readPermission" : "evernote.permission.READ_DATA",
				"writePermission" : "evernote.permission.WRITE_DATA",
				"name" : "com.evernote.provider.EvernoteProvider",
				"grantUriPermissions" : "true"
			}
		}
	],
	"activities_aliases" : [
		{
			"activity-alias" : {
				"name" : "com.evernote.app.CreateShortcuts",
				"targetActivity" : "com.evernote.ui.tablet.NoteListAloneActivity",
				"label" : "@string/note_shortcut"
			}
		}
	],
	"uses_libraries" : [
		{
			"required" : "false",
			"name" : "com.google.android.maps"
		}
	],
	"uses_features" : [
		{
			"required" : "false",
			"name" : "android.hardware.microphone"
		},
		{
			"required" : "false",
			"name" : "android.hardware.location.gps"
		},
		{
			"required" : "false",
			"name" : "android.hardware.faketouch"
		},
		{
			"required" : "false",
			"name" : "android.hardware.touchscreen"
		},
		{
			"required" : "false",
			"name" : "android.hardware.camera"
		},
		{
			"required" : "false",
			"name" : "android.hardware.camera.autofocus"
		},
		{
			"required" : "false",
			"name" : "android.hardware.screen.portrait"
		}
	],
	"version_code" : "15020",
	"supports_screens" : [
		{
			"anyDensity" : "true",
			"normalScreens" : "true",
			"smallScreens" : "true",
			"xlargeScreens" : "true",
			"largeScreens" : "true"
		}
	],
	"package" : "com.evernote",
	"install_location" : "auto",
	"application" : {
		"hardwareAccelerated" : "true",
		"name" : "com.evernote.Evernote",
		"label" : "@string/app_name",
		"debuggable" : "false",
		"largeHeap" : "true",
		"icon" : "@drawable/ic_launcher"
	},
	"meta_data" : [
		{
			"name" : "to.dualscreen",
			"value" : "true"
		}
	],
	"services" : [
		{
			"service" : {
				"name" : "com.evernote.client.EvernoteService",
				"label" : "@string/app_name"
			}
		},
		{
			"service" : {
				"name" : "com.evernote.client.SyncService",
				"label" : "@string/app_name"
			}
		},
		{
			"service" : {
				"name" : "com.evernote.client.tracker.TrackerService"
			}
		},
		{
			"service" : {
				"name" : "com.evernote.billing.BillingService"
			}
		},
		{
			"service" : {
				"name" : "com.evernote.smart.noteworthy.EventsUpdaterService",
				"label" : "test"
			}
		}
	],
	"uses_permissions" : [
		{
			"name" : "com.android.vending.BILLING"
		},
		{
			"name" : "evernote.permission.READ_DATA"
		},
		{
			"name" : "evernote.permission.WRITE_DATA"
		},
		{
			"name" : "android.permission.INTERNET"
		},
		{
			"name" : "android.permission.RECORD_AUDIO"
		},
		{
			"name" : "android.permission.ACCESS_NETWORK_STATE"
		},
		{
			"name" : "android.permission.ACCESS_COARSE_LOCATION"
		},
		{
			"name" : "android.permission.ACCESS_FINE_LOCATION"
		},
		{
			"name" : "android.permission.READ_CONTACTS"
		},
		{
			"name" : "android.permission.VIBRATE"
		},
		{
			"name" : "android.permission.WRITE_EXTERNAL_STORAGE"
		},
		{
			"name" : "android.permission.READ_PHONE_STATE"
		},
		{
			"name" : "android.permission.WAKE_LOCK"
		},
		{
			"name" : "android.permission.ACCESS_WIFI_STATE"
		},
		{
			"name" : "android.permission.GET_ACCOUNTS"
		},
		{
			"name" : "com.android.launcher.permission.INSTALL_SHORTCUT"
		},
		{
			"name" : "android.permission.READ_LOGS"
		},
		{
			"name" : "android.permission.READ_CALENDAR"
		},
		{
			"name" : "android.permission.CAMERA"
		},
		{
			"name" : "android.permission.RECEIVE_BOOT_COMPLETED"
		}
	],
	"version_name" : "5.0.2",
	"receivers" : [
		{
			"receiver" : {
				"name" : "com.evernote.BootReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.ui.helper.SyncNotification"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.ui.helper.LiveKeyAudioNoteReceiver",
				"label" : "@string/start_audio_note"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.ui.helper.StopAudioNoteReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.billing.BillingReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.billing.BillingService$BillingAlarmReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.client.InactivityReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.util.ReferralTrackingReceiver",
				"exported" : "true"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.util.MultiUseReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.amazon.inapp.purchasing.ResponseReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.common.util.AndroidCommonReceiver"
			}
		},
		{
			"receiver" : {
				"name" : "com.evernote.util.SessionTrackingReceiver"
			}
		},
		{
			"receiver" : {
				"process" : ":camera",
				"name" : "com.evernote.android.multishotcamera.BCTransformReceiver"
			}
		}
	],
	"permissions" : [
		{
			"label" : "@string/read_data_label",
			"description" : "evernote.permission.READ_DATA",
			"protectionLevel" : "normal",
			"name" : "evernote.permission.READ_DATA"
		},
		{
			"label" : "@string/write_data_label",
			"description" : "evernote.permission.WRITE_DATA",
			"protectionLevel" : "normal",
			"name" : "evernote.permission.WRITE_DATA"
		}
	]
}
```
