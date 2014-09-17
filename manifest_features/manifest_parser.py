import xml.sax
from xml.sax import ContentHandler
from xml.sax import SAXException
from xml.sax import SAXParseException
from android_manifest import AndroidManifest
from helpers.intent_filter import IntentFilter
from helpers.meta_data import MetaData
from helpers.grant_uri_permission import GrantUriPermission
from helpers.path_permission import PathPermission


class ManifestParser(ContentHandler):
    flags = dict.fromkeys([
                              'in_manifest', 'in_uses_permission',
                              'in_permission', 'in_permission_tree',
                              'in_permission_group', 'in_instrumentation',
                              'in_uses_sdk', 'in_uses_configuration',
                              'in_uses_feature', 'in_supports_screens',
                              'in_compatible_screens',
                              'in_supports_gl_texture',
                              'in_application', 'in_activity',
                              'in_intent_filter',
                              'in_action', 'in_category', 'in_data',
                              'in_meta_data', 'in_activity_alias',
                              'in_service', 'in_receiver', 'in_provider',
                              'in_grant_uri_permission', 'in_path_permission',
                              'in_uses_library'
                          ], False)

    def __init__(self):
        ContentHandler.__init__(self)

        # <activity> global variables
        self.activity_allowTaskReparenting = None
        self.activity_alwaysRetainTaskState = None
        self.activity_clearTaskOnLaunch = None
        self.activity_configChanges = None
        self.activity_enabled = None
        self.activity_excludeFromRecents = None
        self.activity_exported = None
        self.activity_finishOnTaskLaunch = None
        self.activity_hardwareAccelerated = None
        self.activity_icon = None
        self.activity_label = None
        self.activity_launchMode = None
        self.activity_multiprocess = None
        self.activity_name = None
        self.activity_noHistory = None
        self.activity_parentActivityName = None
        self.activity_permission = None
        self.activity_process = None
        self.activity_screenOrientation = None
        self.activity_stateNotNeeded = None
        self.activity_taskAffinity = None
        self.activity_theme = None
        self.activity_uiOptions = None
        self.activity_windowSoftInputMode = None
        # end of <activity> global variables

        # <activity-alias> global variables
        self.activity_alias_enabled = None
        self.activity_alias_exported = None
        self.activity_alias_icon = None
        self.activity_alias_label = None
        self.activity_alias_name = None
        self.activity_alias_permission = None
        self.activity_alias_targetActivity = None
        # end of <activity-alias> global variables

        # <service> global variables
        self.service_enabled = None
        self.service_exported = None
        self.service_icon = None
        self.service_isolatedProcess = None
        self.service_label = None
        self.service_name = None
        self.service_permission = None
        self.service_process = None
        # end of <service> global variables

        # <provider> global variables
        self.provider_authorities = None
        self.provider_enabled = None
        self.provider_exported = None
        self.provider_grantUriPermissions = None
        self.provider_icon = None
        self.provider_initOrder = None
        self.provider_label = None
        self.provider_multiprocess = None
        self.provider_name = None
        self.provider_permission = None
        self.provider_process = None
        self.provider_readPermission = None
        self.provider_syncable = None
        self.provider_writePermission = None
        # end of <provider> global variables

        # <receiver> global elemnts
        self.receiver_enabled = None
        self.receiver_exported = None
        self.receiver_icon = None
        self.receiver_label = None
        self.receiver_name = None
        self.receiver_permission = None
        self.receiver_process = None
        # end of <receiver> global elemnts

        self.app_manifest = None

        self.intent_filter_activity = None
        self.intent_filter_activity_alias = None
        self.intent_filter_service = None
        self.intent_filter_receiver = None

        self.meta_data_application = []
        self.meta_data_activity = []
        self.meta_data_activity_alias = []
        self.meta_data_service = []
        self.meta_data_provider = []
        self.meta_data_receiver = []
        self.grant_uri_permission = []
        self.path_permission = []
        self.unrecognized = False

    def startElement(self, name, attrs):
        # Wait for the end of unrecognized elements to parsing invalid elements.
        if self.unrecognized:
            return
        if name == 'manifest':
            self.flags['in_manifest'] = True
            self.do_manifest(attrs)
        elif name == 'uses-permission':
            self.flags['in_uses_permission'] = True
            self.do_uses_permission(attrs)
        elif name == 'permission':
            self.flags['in_permission'] = True
            self.do_permission(attrs)
        elif name == 'permission-tree':
            self.flags['in_permission_tree'] = True
            self.do_permission_tree(attrs)
        elif name == 'permission-group':
            self.flags['in_permission_group'] = True
            self.do_permission_group(attrs)
        elif name == 'instrumentation':
            self.flags['in_instrumentation'] = True
            self.do_instrumentation(attrs)
        elif name == 'uses-sdk':
            self.flags['in_uses_sdk'] = True
            self.do_uses_sdk(attrs)
        elif name == 'uses-configuration':
            self.flags['in_uses_configuration'] = True
            self.do_uses_configuration(attrs)
        elif name == 'uses-feature':
            self.flags['in_uses_feature'] = True
            self.do_uses_feature(attrs)
        elif name == 'supports-screens':
            self.flags['in_supports_screens'] = True
            self.do_supports_screens(attrs)
        elif name == 'compatible-screens':
            self.flags['in_compatible_screens'] = True
            self.do_compatible_screens(attrs)
        elif name == 'supports-gl-texture':
            self.flags['in_supports_gl_texture'] = True
            self.do_supports_gl_texture(attrs)
        elif name == 'application':
            self.flags['in_application'] = True
            self.do_application(attrs)
        elif name == 'activity':
            self.flags['in_activity'] = True
            self.do_activity(attrs)
        elif name == 'intent-filter':
            self.flags['in_intent_filter'] = True
            self.do_intent_filter(attrs)
        elif name == 'action':
            self.flags['in_action'] = True
            self.do_action(attrs)
        elif name == 'category':
            self.flags['in_category'] = True
            self.do_category(attrs)
        elif name == 'data':
            self.flags['in_data'] = True
            self.do_data(attrs)
        elif name == 'meta-data':
            self.flags['in_meta_data'] = True
            self.do_meta_data(attrs)
        elif name == 'activity-alias':
            self.flags['in_activity_alias'] = True
            self.do_activity_alias(attrs)
        elif name == 'service':
            self.flags['in_service'] = True
            self.do_service(attrs)
        elif name == 'receiver':
            self.flags['in_receiver'] = True
            self.do_receiver(attrs)
        elif name == 'provider':
            self.flags['in_provider'] = True
            self.do_provider(attrs)
        elif name == 'grant-uri-permission':
            self.flags['in_grant_uri_permission'] = True
            self.do_grant_uri_permission(attrs)
        elif name == 'path-permission':
            self.flags['in_path_permission'] = True
            self.do_path_permission(attrs)
        elif name == 'uses-library':
            self.flags['in_uses_library'] = True
            self.do_uses_library(attrs)
        else:
            print("Error: Unrecognized XML element " + name)
            # This is important because some manifest files contain typos making unrecognized elements
            self.unrecognized = True

    def endElement(self, name):
        if name == 'in_manifest':
            self.flags['in_manifest'] = False
        elif name == 'in_uses_permission':
            self.flags['in_uses_permission'] = False
        elif name == 'permission':
            self.flags['in_permission'] = False
        elif name == 'permission-tree':
            self.flags['in_permission_tree'] = False
        elif name == 'permission-group':
            self.flags['in_permission_group'] = False
        elif name == 'instrumentation':
            self.flags['in_instrumentation'] = False
        elif name == 'uses-sdk':
            self.flags['in_uses_sdk'] = False
        elif name == 'uses-configuration':
            self.flags['in_uses_configuration'] = False
        elif name == 'uses-feature':
            self.flags['in_uses_feature'] = False
        elif name == 'supports-screens':
            self.flags['in_supports_screens'] = False
        elif name == 'compatible-screens':
            self.flags['in_compatible_screens'] = False
        elif name == 'supports-gl-texture':
            self.flags['in_supports_gl_texture'] = False
        elif name == 'application':
            self.flags['in_application'] = False
            self.app_manifest.set_application_meta_data(
                self.meta_data_application)
        elif name == 'activity':
            self.do_end_activity()
            self.reset_activity_variables()
            self.flags['in_activity'] = False
            self.intent_filter_activity = None
            self.meta_data_activity = []
        elif name == 'intent-filter':
            self.flags['in_intent_filter'] = False
        elif name == 'action':
            self.flags['in_action'] = False
        elif name == 'category':
            self.flags['in_category'] = False
        elif name == 'data':
            self.flags['in_data'] = False
        elif name == 'meta-data':
            self.flags['in_meta_data'] = False
        elif name == 'activity-alias':
            self.do_end_activity_alias()
            self.reset_activity_alias_variables()
            self.flags['in_activity_alias'] = False
            self.intent_filter_activity_alias = None
            self.meta_data_activity_alias = []
        elif name == 'service':
            self.do_end_service()
            self.reset_service_variables()
            self.flags['in_service'] = False
            self.intent_filter_service = None
            self.meta_data_service = []
        elif name == 'receiver':
            self.do_end_receiver()
            self.reset_receiver_variables()
            self.flags['in_receiver'] = False
            self.intent_filter_receiver = None
            self.meta_data_receiver = []
        elif name == 'provider':
            self.do_end_provider()
            self.reset_provider_variables()
            self.flags['in_provider'] = False
        elif name == 'grant-uri-permission':
            self.flags['in_grant_uri_permission'] = False
        elif name == 'path-permission':
            self.flags['in_path_permission'] = False
        elif name == 'uses-library':
            self.flags['uses_library'] = False
        else:
            self.unrecognized = False

    # Get element's content
    def characters(self, content):
        if self.flags['in_activity']:
            return

    def reset_activity_variables(self):
        self.activity_allowTaskReparenting = None
        self.activity_alwaysRetainTaskState = None
        self.activity_clearTaskOnLaunch = None
        self.activity_configChanges = None
        self.activity_enabled = None
        self.activity_excludeFromRecents = None
        self.activity_exported = None
        self.activity_finishOnTaskLaunch = None
        self.activity_hardwareAccelerated = None
        self.activity_icon = None
        self.activity_label = None
        self.activity_launchMode = None
        self.activity_multiprocess = None
        self.activity_name = None
        self.activity_noHistory = None
        self.activity_parentActivityName = None
        self.activity_permission = None
        self.activity_process = None
        self.activity_screenOrientation = None
        self.activity_stateNotNeeded = None
        self.activity_taskAffinity = None
        self.activity_theme = None
        self.activity_uiOptions = None
        self.activity_windowSoftInputMode = None

    def reset_activity_alias_variables(self):
        self.activity_alias_enabled = None
        self.activity_alias_exported = None
        self.activity_alias_icon = None
        self.activity_alias_label = None
        self.activity_alias_name = None
        self.activity_alias_permission = None
        self.activity_alias_targetActivity = None

    def reset_service_variables(self):
        self.service_enabled = None
        self.service_exported = None
        self.service_icon = None
        self.service_isolatedProcess = None
        self.service_label = None
        self.service_name = None
        self.service_permission = None
        self.service_process = None

    def reset_receiver_variables(self):
        self.receiver_enabled = None
        self.receiver_exported = None
        self.receiver_icon = None
        self.receiver_label = None
        self.receiver_name = None
        self.receiver_permission = None
        self.receiver_process = None

    def reset_provider_variables(self):
        self.provider_authorities = None
        self.provider_enabled = None
        self.provider_exported = None
        self.provider_grantUriPermissions = None
        self.provider_icon = None
        self.provider_initOrder = None
        self.provider_label = None
        self.provider_multiprocess = None
        self.provider_name = None
        self.provider_permission = None
        self.provider_process = None
        self.provider_readPermission = None
        self.provider_syncable = None
        self.provider_writePermission = None

    def do_manifest(self, attrs):
        package = attrs.get('package', None)
        sharedUserId = attrs.get('android:sharedUserId', None)
        sharedUserLabel = attrs.get('android:sharedUserLabel', None)
        versionCode = attrs.get('android:versionCode', None)
        versionName = attrs.get('android:versionName', None)
        installLocation = attrs.get('android:installLocation', None)
        self.app_manifest = AndroidManifest(package, sharedUserId,
                                            sharedUserLabel, versionCode,
                                            versionName, installLocation)

    def do_uses_permission(self, attrs):
        name = attrs.get('android:name', None)
        max_sdk_version = attrs.get('android:maxSdkVersion', None)
        self.app_manifest.set_uses_permission(name, max_sdk_version)

    def do_permission(self, attrs):
        description = attrs.get('android:name', None)
        icon = attrs.get('android:icon', None)
        label = attrs.get('android:label', None)
        name = attrs.get('android:name', None)
        permission_group = attrs.get('android:permissionGroup', None)
        protection_level = attrs.get('android:protectionLevel', None)
        self.app_manifest.set_permission(description, icon, label, name,
                                         permission_group, protection_level)

    def do_permission_tree(self, attrs):
        icon = attrs.get('android:icon', None)
        label = attrs.get('android:label', None)
        name = attrs.get('android:name', None)
        self.app_manifest.set_permission_tree(icon, label, name)

    def do_permission_group(self, attrs):
        description = attrs.get('android:name', None)
        icon = attrs.get('android:icon', None)
        label = attrs.get('android:label', None)
        name = attrs.get('android:name', None)
        self.app_manifest.set_permission_group(description, icon, label, name)

    def do_instrumentation(self, attrs):
        functional_test = attrs.get('android:functionalTest', None)
        handle_profiling = attrs.get('android:handleProfiling', None)
        icon = attrs.get('android:icon', None)
        label = attrs.get('android:label', None)
        name = attrs.get('android:name', None)
        target_package = attrs.get('android:targetPackage', None)
        self.app_manifest.set_instrumentation(functional_test,
                                              handle_profiling, icon, label,
                                              name, target_package)

    def do_uses_sdk(self, attrs):
        min_sdk_version = attrs.get('android:minSdkVersion', None)
        target_sdk_version = attrs.get('android:targetSdkVersion', None)
        max_sdk_version = attrs.get('android:maxSdkVersion', None)
        self.app_manifest.set_uses_sdk(min_sdk_version, target_sdk_version,
                                       max_sdk_version)

    def do_uses_configuration(self, attrs):
        req_five_way_nav = attrs.get('android:reqFiveWayNav', None)
        req_hard_keyboard = attrs.get('android:reqHardKeyboard', None)
        req_keyboard_type = attrs.get('android:reqKeyboardType', None)
        req_navigation = attrs.get('android:reqNavigation', None)
        req_touch_screen = attrs.get('android:reqTouchScreen', None)
        self.app_manifest.set_uses_configuration(req_five_way_nav,
                                                 req_hard_keyboard,
                                                 req_keyboard_type,
                                                 req_navigation,
                                                 req_touch_screen)

    def do_uses_feature(self, attrs):
        name = attrs.get('android:name', None)
        required = attrs.get('android:required', None)
        gl_es_version = attrs.get('android:glEsVersion', None)
        self.app_manifest.set_uses_features(name, required, gl_es_version)

    def do_supports_screens(self, attrs):
        resizeable = attrs.get('android:resizeable', None)
        small_screens = attrs.get('android:smallScreens', None)
        normal_screens = attrs.get('android:normalScreens', None)
        large_screens = attrs.get('android:largeScreens', None)
        xlarge_screens = attrs.get('android:xlargeScreens', None)
        any_density = attrs.get('android:anyDensity', None)
        requires_smallest_width_dp = attrs.get(
            'android:requiresSmallestWidthDp', None)
        compatible_width_limit_dp = attrs.get('android:compatibleWidthLimitDp',
                                              None)
        largest_width_limit_dp = attrs.get('android:largestWidthLimitDp', None)
        self.app_manifest.set_supports_screens(resizeable, small_screens,
                                               normal_screens, large_screens,
                                               xlarge_screens, any_density,
                                               requires_smallest_width_dp,
                                               compatible_width_limit_dp,
                                               largest_width_limit_dp)

    def do_compatible_screens(self, attrs):
        screen_size = attrs.get('android:screenSize', None)
        screen_density = attrs.get('android:screenDensity', None)
        self.app_manifest.set_compatible_screens(screen_size, screen_density)

    def do_supports_gl_texture(self, attrs):
        name = attrs.get('android:name', None)
        self.app_manifest.set_supports_gl_texture(name)

    def do_application(self, attrs):
        allowTaskReparenting = attrs.get('android:allowTaskReparenting', None)
        allowBackup = attrs.get('android:allowbackup', None)
        backupAgent = attrs.get('android:backupAgent', None)
        debuggable = attrs.get('android:debuggable', None)
        description = attrs.get('android:description', None)
        enabled = attrs.get('android:enabled', None)
        hasCode = attrs.get('android:hasCode', None)
        hardwareAccelerated = attrs.get('android:hardwareAccelerated', None)
        icon = attrs.get('android:icon', None)
        killAfterRestore = attrs.get('android:killAfterRestore', None)
        label = attrs.get('android:label', None)
        logo = attrs.get('android:logo', None)
        manageSpaceActivity = attrs.get('android:manageSpaceActivity', None)
        largeHeap = attrs.get('android:largeHeap', None)
        name = attrs.get('android:name', None)
        permission = attrs.get('android:permission', None)
        persistent = attrs.get('android:persistent', None)
        process = attrs.get('android:process', None)
        restoreAnyVersion = attrs.get('android:restoreAnyVersion', None)
        requiredAccountType = attrs.get('android:requiredAccountType', None)
        restrictedAccountType = attrs.get('android:restrictedAccountType',
                                          None)
        supportsRtl = attrs.get('android:supportsRtl', None)
        taskAffinity = attrs.get('android:taskAffinity', None)
        testOnly = attrs.get('android:testOnly', None)
        theme = attrs.get('android:theme', None)
        uiOptions = attrs.get('android:uiOptions', None)
        vmSafeMode = attrs.get('android:vmSafeMode', None)
        self.app_manifest.set_application(allowTaskReparenting, allowBackup,
                                          backupAgent, debuggable,
                                          description, enabled, hasCode,
                                          hardwareAccelerated, icon,
                                          killAfterRestore,
                                          label, logo, manageSpaceActivity,
                                          largeHeap, name, permission,
                                          persistent,
                                          process, restoreAnyVersion,
                                          requiredAccountType,
                                          restrictedAccountType,
                                          supportsRtl, taskAffinity, testOnly,
                                          theme,
                                          uiOptions, vmSafeMode)

    def do_activity(self, attrs):
        self.activity_allowTaskReparenting = attrs.get(
            'android:allowTaskReparenting', None)
        self.activity_alwaysRetainTaskState = attrs.get(
            'android:alwaysRetainTaskState', None)
        self.activity_clearTaskOnLaunch = attrs.get(
            'android:clearTaskOnLaunch', None)
        self.activity_configChanges = attrs.get('android:configChanges', None)
        self.activity_enabled = attrs.get('android:enabled', None)
        self.activity_excludeFromRecents = attrs.get(
            'android:excludeFromRecents', None)
        self.activity_exported = attrs.get('android:exported', None)
        self.activity_finishOnTaskLaunch = attrs.get(
            'android:finishOnTaskLaunch', None)
        self.activity_hardwareAccelerated = attrs.get(
            'android:hardwareAccelerated', None)
        self.activity_icon = attrs.get('android:icon', None)
        self.activity_label = attrs.get('android:label', None)
        self.activity_launchMode = attrs.get('android:launchMode', None)
        self.activity_multiprocess = attrs.get('android:multiprocess', None)
        self.activity_name = attrs.get('android:name', None)
        self.activity_noHistory = attrs.get('android:noHistory', None)
        self.activity_parentActivityName = attrs.get(
            'android:parentActivityName', None)
        self.activity_permission = attrs.get('android:permission', None)
        self.activity_process = attrs.get('android:process', None)
        self.activity_screenOrientation = attrs.get(
            'android:screenOrientation', None)
        self.activity_stateNotNeeded = attrs.get('android:stateNotNeeded',
                                                 None)
        self.activity_taskAffinity = attrs.get('android:taskAffinity', None)
        self.activity_theme = attrs.get('android:theme', None)
        self.activity_uiOptions = attrs.get('android:uiOptions', None)
        self.activity_windowSoftInputMode = attrs.get(
            'android:windowSoftInputMode', None)

    def do_end_activity(self):
        self.app_manifest.set_activity(self.activity_allowTaskReparenting,
                                       self.activity_alwaysRetainTaskState,
                                       self.activity_clearTaskOnLaunch,
                                       self.activity_configChanges,
                                       self.activity_enabled,
                                       self.activity_excludeFromRecents,
                                       self.activity_exported,
                                       self.activity_finishOnTaskLaunch,
                                       self.activity_hardwareAccelerated,
                                       self.activity_icon, self.activity_label,
                                       self.activity_launchMode,
                                       self.activity_multiprocess,
                                       self.activity_name,
                                       self.activity_noHistory,
                                       self.activity_parentActivityName,
                                       self.activity_permission,
                                       self.activity_process,
                                       self.activity_screenOrientation,
                                       self.activity_stateNotNeeded,
                                       self.activity_taskAffinity,
                                       self.activity_theme,
                                       self.activity_uiOptions,
                                       self.activity_windowSoftInputMode,
                                       self.intent_filter_activity,
                                       self.meta_data_activity)

    def do_intent_filter(self, attrs):
        name = attrs.get('android:name', None)
        icon = attrs.get('android:icon', None)
        label = attrs.get('android:label', None)
        priority = attrs.get('android:priority', None)
        if self.flags['in_activity']:
            self.intent_filter_activity = IntentFilter(name, icon, label,
                                                       priority)
        elif self.flags['in_activity_alias']:
            self.intent_filter_activity_alias = IntentFilter(name, icon, label,
                                                             priority)
        elif self.flags['in_service']:
            self.intent_filter_service = IntentFilter(name, icon, label,
                                                      priority)
        elif self.flags['in_receiver']:
            self.intent_filter_receiver = IntentFilter(name, icon, label,
                                                       priority)

    def do_action(self, attrs):
        # <action android:name="string" /> is only contained in
        # <intent-filter> element
        if self.flags['in_intent_filter'] == False:
            return
        if self.flags['in_action'] and self.flags['in_activity']:
            self.intent_filter_activity.set_action(
                attrs.get('android:name', None))
        elif self.flags['in_action'] and self.flags['in_activity_alias']:
            self.intent_filter_activity_alias.set_action(
                attrs.get('android:name', None))
        elif self.flags['in_action'] and self.flags['in_service']:
            self.intent_filter_service.set_action(
                attrs.get('android:name', None))
        elif self.flags['in_action'] and self.flags['in_receiver']:
            self.intent_filter_receiver.set_action(
                attrs.get('android:name', None))

    def do_category(self, attrs):
        # <category android:name="string" /> is only contained in
        # <intent-filter> element
        if self.flags['in_intent_filter'] == False:
            return
        if self.flags['in_category'] and self.flags['in_activity']:
            self.intent_filter_activity.set_category(
                attrs.get('android:name', None))
        elif self.flags['in_category'] and self.flags['in_activity_alias']:
            self.intent_filter_activity_alias.set_category(
                attrs.get('android:name', None))
        elif self.flags['in_category'] and self.flags['in_service']:
            self.intent_filter_service.set_category(
                attrs.get('android:name', None))
        elif self.flags['in_category'] and self.flags['in_receiver']:
            self.intent_filter_receiver.set_category(
                attrs.get('android:name', None))

    def do_data(self, attrs):
        # <data android:host="string"... /> is only contained in
        # <intent-filter> element
        if self.flags['in_intent_filter'] == False:
            return
        scheme = attrs.get('android:scheme', None)
        host = attrs.get('android:host', None)
        path = attrs.get('android:path', None)
        port = attrs.get('android:port', None)
        pathPrefix = attrs.get('android:pathPrefix', None)
        pathPattern = attrs.get('android:pathPattern', None)
        mimeType = attrs.get('android:mimeType', None)

        if self.flags['in_data'] and self.flags['in_activity']:
            self.intent_filter_activity.set_data(scheme, host, port, path,
                                                 pathPattern, pathPrefix,
                                                 mimeType)
        elif self.flags['in_data'] and self.flags['in_activity_alias']:
            self.intent_filter_activity_alias.set_data(scheme, host, port,
                                                       path, pathPattern,
                                                       pathPrefix, mimeType)
        elif self.flags['in_data'] and self.flags['in_service']:
            self.intent_filter_service.set_data(scheme, host, port, path,
                                                pathPattern, pathPrefix,
                                                mimeType)
        elif self.flags['in_data'] and self.flags['in_receiver']:
            self.intent_filter_receiver.set_data(scheme, host, port, path,
                                                 pathPattern, pathPrefix,
                                                 mimeType)

    def do_meta_data(self, attrs):
        # <meta-data is contained in: <activity>, <activity-alias>,
        # <application>, <provider>, <receiver>
        name = attrs.get('android:name', None)
        resource = attrs.get('android:resource', None)
        value = attrs.get('android:value', None)

        if self.flags['in_meta_data'] and self.flags['in_activity']:
            self.meta_data_activity.append(MetaData(name, resource, value))
        elif self.flags['in_meta_data'] and self.flags['in_activity_alias']:
            self.meta_data_activity_alias.append(
                MetaData(name, resource, value))
        elif self.flags['in_meta_data'] and self.flags['in_service']:
            self.meta_data_service.append(MetaData(name, resource, value))
        elif self.flags['in_meta_data'] and self.flags['in_receiver']:
            self.meta_data_receiver.append(MetaData(name, resource, value))
        elif self.flags['in_meta_data'] and self.flags['in_provider']:
            self.meta_data_provider.append(MetaData(name, resource, value))
        elif self.flags['in_meta_data'] and self.flags['in_application']:
            self.meta_data_application.append(MetaData(name, resource, value))

    def do_activity_alias(self, attrs):
        self.activity_alias_enabled = attrs.get('android:enabled', None)
        self.activity_alias_exported = attrs.get('android:exported', None)
        self.activity_alias_icon = attrs.get('android:icon', None)
        self.activity_alias_label = attrs.get('android:label', None)
        self.activity_alias_name = attrs.get('android:name', None)
        self.activity_alias_permission = attrs.get('android:permission', None)
        self.activity_alias_targetActivity = attrs.get(
            'android:targetActivity', None)

    def do_end_activity_alias(self):
        self.app_manifest.set_activity_alias(
            self.activity_alias_enabled,
            self.activity_alias_exported,
            self.activity_alias_icon,
            self.activity_alias_label,
            self.activity_alias_name,
            self.activity_alias_permission,
            self.activity_alias_targetActivity,
            self.intent_filter_activity_alias,
            self.meta_data_activity_alias)

    def do_service(self, attrs):
        self.service_enabled = attrs.get('android:enabled', None)
        self.service_exported = attrs.get('android:exported', None)
        self.service_icon = attrs.get('android:icon', None)
        self.service_isolatedProcess = attrs.get('android:isolatedProcess',
                                                 None)
        self.service_label = attrs.get('android:label', None)
        self.service_name = attrs.get('android:name', None)
        self.service_permission = attrs.get('android:permission', None)
        self.service_process = attrs.get('android:process', None)

    def do_end_service(self):
        self.app_manifest.set_service(self.service_enabled,
                                      self.service_exported,
                                      self.service_icon,
                                      self.service_isolatedProcess,
                                      self.service_label, self.service_name,
                                      self.service_permission,
                                      self.service_process,
                                      self.intent_filter_service,
                                      self.meta_data_service)

    def do_receiver(self, attrs):
        self.receiver_enabled = attrs.get('android:enabled', None)
        self.receiver_exported = attrs.get('android:exported', None)
        self.receiver_icon = attrs.get('android:icon', None)
        self.receiver_label = attrs.get('android:label', None)
        self.receiver_name = attrs.get('android:name', None)
        self.receiver_permission = attrs.get('android:permission', None)
        self.receiver_process = attrs.get('android:process', None)

    def do_end_receiver(self):
        self.app_manifest.set_receiver(self.receiver_enabled,
                                       self.receiver_exported,
                                       self.receiver_icon, self.receiver_label,
                                       self.receiver_name,
                                       self.receiver_permission,
                                       self.receiver_process,
                                       self.intent_filter_receiver,
                                       self.meta_data_receiver)

    def do_provider(self, attrs):
        self.provider_authorities = attrs.get('android:authorities', None)
        self.provider_enabled = attrs.get('android:enabled', None)
        self.provider_exported = attrs.get('android:exported', None)
        self.provider_grantUriPermissions = attrs.get(
            'android:grantUriPermissions', None)
        self.provider_icon = attrs.get('android:icon', None)
        self.provider_initOrder = attrs.get('android:initOrder', None)
        self.provider_label = attrs.get('android:label', None)
        self.provider_multiprocess = attrs.get('android:multiprocess', None)
        self.provider_name = attrs.get('android:name', None)
        self.provider_permission = attrs.get('android:permission', None)
        self.provider_process = attrs.get('android:process', None)
        self.provider_readPermission = attrs.get('android:readPermission',
                                                 None)
        self.provider_syncable = attrs.get('android:syncable', None)
        self.provider_writePermission = attrs.get('android:writePermission',
                                                  None)

    def do_end_provider(self):
        self.app_manifest.set_provider(self.provider_authorities,
                                       self.provider_enabled,
                                       self.provider_exported,
                                       self.provider_grantUriPermissions,
                                       self.provider_icon,
                                       self.provider_initOrder,
                                       self.provider_label,
                                       self.provider_multiprocess,
                                       self.provider_name,
                                       self.provider_permission,
                                       self.provider_process,
                                       self.provider_readPermission,
                                       self.provider_syncable,
                                       self.provider_writePermission,
                                       self.meta_data_provider,
                                       self.grant_uri_permission,
                                       self.path_permission)

    def do_grant_uri_permission(self, attrs):
        path = attrs.get('android:path')
        pathPattern = attrs.get('android:pathPattern')
        pathPrefix = attrs.get('android:pathPrefix')
        self.grant_uri_permission.append(
            GrantUriPermission(path, pathPattern, pathPrefix))

    def do_path_permission(self, attrs):
        path = attrs.get('android:path', None)
        pathPrefix = attrs.get('android:pathPrefix', None)
        pathPattern = attrs.get('android:pathPattern', None)
        permission = attrs.get('android:permission', None)
        readPermission = attrs.get('android:readPermission', None)
        writePermission = attrs.get('android:writePermission', None)
        self.path_permission.append(
            PathPermission(path, pathPrefix, pathPattern, permission,
                           readPermission,
                           writePermission))

    def do_uses_library(self, attrs):
        name = attrs.get('android:name', None)
        required = attrs.get('android:required', None)
        self.app_manifest.set_uses_library(name, required)

    def parse(self, source):
        try:
            xml.sax.parse(source, self)
        except (SAXException, SAXParseException) as e:
            return None
        return self.app_manifest
