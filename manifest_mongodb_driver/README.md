# AndroidManifest MongoDB Python Driver
This is the MongoDB driver for the database. It retrieves manifest features by the app name and version number. The results are stored into text files.
### Usage
```
Usage: manifest_driver.py [options] {find_app_activities} out_dir

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -p PACKAGE_NAME, --package=PACKAGE_NAME
                        App package name.
  -r APP_VERSION, --ver=APP_VERSION
                        App version name.
  -l FILE, --log=FILE   write logs to FILE.
  -v, --verbose         Increase verbosity.
```
### Example

``` 
$ python ./manifest_driver.py find_app_activities ./ -p com.evernote -r 5.0.2
$ cat ./com.evernote-5.0.2-activities.txt

[Main] com.evernote.ui.HomeActivity
com.evernote.ui.phone.PhoneMainActivity
com.evernote.ui.tablet.TabletMainActivity
com.evernote.ui.ShortcutsActivity
com.evernote.ui.maps.EvernoteMapActivity
com.evernote.ui.maps.SnippetActivity
com.evernote.ui.maps.NoteListActivity
com.evernote.ui.maps.MapActivityGroup
com.evernote.ui.maps.PinDropActivity
com.evernote.ui.maps.amazon.EvernoteMapActivity
com.evernote.ui.maps.amazon.MapActivityGroup
com.evernote.ui.maps.amazon.PinDropActivity
com.evernote.ui.PinLockActivity
com.evernote.ui.SecurityPreferenceActivity
com.evernote.ui.phone.SwipeableNoteListActivity
com.evernote.ui.phone.SwipeableNoteListAloneActivity
com.evernote.ui.EvernoteNotePickerActivity
com.evernote.ui.phone.SwipeableNoteViewActivity
com.evernote.ui.phone.HoneycombSwipeableNoteViewActivity
com.evernote.ui.phone.SwipeableNoteViewAloneActivity
com.evernote.ui.InformationActivity
com.evernote.ui.tablet.NoteListActivity
com.evernote.ui.GoogleSearchResultRedirectActivity
com.evernote.ui.tablet.NoteListAloneActivity
com.evernote.ui.tablet.NoteViewActivity
com.evernote.ui.tablet.NoteViewAloneActivity
com.evernote.ui.AccountInfoPreferenceActivity
com.evernote.ui.EvernotePreferenceActivity
com.evernote.note.composer.NewNoteActivity
com.evernote.ui.SkitchImageActivity
com.evernote.note.composer.NewNoteAloneActivity
com.evernote.ui.WidgetNewNoteActivity
com.evernote.ui.EmailActivity
com.evernote.ui.TagEditActivity
com.evernote.ui.NoteInfoActivity
com.evernote.ui.SkitchUpsellActivity
com.evernote.note.composer.FilePickerActivity
com.evernote.ui.AuthenticationActivity
com.evernote.ui.WebActivity
com.evernote.ui.TrunkActivity
com.evernote.ui.SearchActivity
com.evernote.ui.WidgetSearchActivity
com.evernote.ui.AdvanceSearchActivity
com.evernote.ui.AdvanceSearchSelector
com.evernote.ui.landing.LandingActivity
com.evernote.ui.RateAppActivity
com.evernote.ui.DYNDialogActivity
com.evernote.ui.StandardDialogActivity
com.evernote.ui.ShareWithFacebook
com.evernote.ui.ShareDialogActivity
com.evernote.ui.SDCardChangedActivity
com.evernote.ui.helper.URIBrokerActivity
com.evernote.billing.AmazonBillingActivity
com.evernote.billing.BillingActivity
com.evernote.billing.BillingHelper$BillingHelperActivity
com.evernote.billing.LaunchBillingActivity
com.evernote.ui.smartnotebook.SmartNotebookSettingsActivity
com.evernote.ui.NotebookShareSettingsActivity
com.evernote.ui.NoteShareSettingsActivity
com.evernote.ui.EmailPickerActivity
com.evernote.support.CustomerSupportActivity
com.evernote.help.FeatureDiscoveryWidgetGet
com.evernote.help.FeatureDiscoveryPromo
com.evernote.help.PromoWebActivity
com.evernote.ui.BusinessLibraryActivity
com.evernote.help.FeatureDiscoveryWidgetConfig
com.evernote.ui.VideoCaptureActivity
com.evernote.ui.WelcomeActivity
com.evernote.ui.UserSetupActivity
com.evernote.ui.gallery.GalleryActivity
com.evernote.smart.noteworthy.EventsActivity
com.evernote.android.multishotcamera.MultiShotCameraActivity
com.evernote.android.multishotcamera.FilePickerActivity
com.evernote.android.multishotcamera.ViewImagesActivity
```