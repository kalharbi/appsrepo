class AndroidManifest(object):
    def __init__(self, package, shared_user_id, shared_user_label,
                 version_code,
                 version_name, install_location):
        self.package = package
        self.shared_user_id = shared_user_id
        self.shared_user_label = shared_user_label
        self.version_code = version_code
        self.version_name = version_name
        self.install_location = install_location
        self.uses_permissions = []
        self.permissions = []
        self.permission_trees = []
        self.permission_groups = []
        self.instrumentations = []
        self.min_sdk_version = None
        self.target_sdk_version = None
        self.max_sdk_version = None
        self.uses_configurations = []
        self.uses_features = []
        self.supports_screens = []
        self.compatible_screens = []
        self.gl_texture = []
        self.application = None
        self.activities = []
        self.activities_aliases = []
        self.services = []
        self.receivers = []
        self.providers = []
        self.meta_data = None  # Only <meta-data> elements inside <application>
        self.uses_libraries = []

    def set_sdk_versions(self, min_sdk_version, target_sdk_version):
        self.min_sdk_version = min_sdk_version
        self.target_sdk_version = target_sdk_version

    def set_uses_permission(self, name=None, max_sdk_version=None):
        uses_permission_set = {'name': name, 'maxSdkVersion': max_sdk_version}
        self.uses_permissions.append(uses_permission_set)

    def set_permission(self, description=None, icon=None, label=None,
                       name=None, permission_group=None,
                       protection_level=None):
        permission_set = {'description': description, 'icon': icon,
                          'label': label, 'name': name,
                          'permissionGroup': permission_group,
                          'protectionLevel': protection_level}
        self.permissions.append(permission_set)

    def set_permission_tree(self, icon=None, label=None, name=None):
        permission_tree_set = {'icon': icon, 'label': label, 'name': name}
        self.permission_trees.append(permission_tree_set)

    def set_permission_group(self, description, icon, label, name):
        permission_group_set = {'description': description, 'icon': icon,
                                'label': label, 'name': name}
        self.permission_groups.append(permission_group_set)

    def set_instrumentation(self, functional_test, handle_profiling, icon,
                            label, name, target_package):
        instrumentation_set = {'functionalTest': functional_test,
                               'handleProfiling': handle_profiling,
                               'icon': icon, 'label': label, 'name': name,
                               'targetPackage': target_package}
        self.instrumentations.append(instrumentation_set)

    def set_uses_sdk(self, min_sdk_version, target_sdk_version,
                     max_sdk_version=None):
        self.min_sdk_version = min_sdk_version
        self.target_sdk_version = target_sdk_version
        self.max_sdk_version = max_sdk_version
    
    def set_uses_min_sdk(self, min_sdk_version):
        self.min_sdk_version = min_sdk_version
    
    def set_uses_max_sdk(self, max_sdk_version):
        self.max_sdk_version = max_sdk_version
        
    def set_uses_target_sdk(self, target_sdk_version):
        self.target_sdk_version = target_sdk_version

    def set_uses_configuration(self, req_five_way_nav, req_hard_keyboard,
                               req_keyboard_type, req_navigation,
                               req_touch_screen):
        uses_configuration_set = {'reqFiveWayNav': req_five_way_nav,
                                  'reqHardKeyboard': req_hard_keyboard,
                                  'reqKeyboardType': req_keyboard_type,
                                  'reqNavigation': req_navigation,
                                  'reqTouchScreen': req_touch_screen}
        self.uses_configurations.append(uses_configuration_set)

    def set_uses_features(self, name, required, gl_es_version):
        uses_features_set = {'name': name, 'required': required,
                             'glEsVersion': gl_es_version}
        self.uses_features.append(uses_features_set)

    def set_supports_screens(self, resizeable, small_screens, normal_screens,
                             large_screens, xlarge_screens,
                             any_density, requires_smallest_width_dp,
                             compatible_width_limit_dp,
                             largest_width_limit_dp):
        supports_screens_set = {
            'resizeable': resizeable,
            'smallScreens': small_screens,
            'normalScreens': normal_screens,
            'largeScreens': large_screens,
            'xlargeScreens': xlarge_screens,
            'anyDensity': any_density,
            'requiresSmallestWidthDp': requires_smallest_width_dp,
            'compatibleWidthLimitDp': compatible_width_limit_dp,
            'largestWidthLimitDp': largest_width_limit_dp}
        self.supports_screens.append(supports_screens_set)

    def set_compatible_screens(self, screen_size, screen_density):
        screen_set = {'screenSize': screen_size,
                      'screenDensity': screen_density}
        inner_list = {'screen': screen_set}
        self.compatible_screens.append(inner_list)

    def set_supports_gl_texture(self, name):
        gl_texture_set = {'name': name}
        self.gl_texture.append(gl_texture_set)

    def set_application(self, allowTaskReparenting, allowBackup, backupAgent,
                        debuggable,
                        description, enabled, hasCode, hardwareAccelerated,
                        icon, killAfterRestore,
                        label, logo, manageSpaceActivity, largeHeap, name,
                        permission, persistent,
                        process, restoreAnyVersion, requiredAccountType,
                        restrictedAccountType,
                        supportsRtl, taskAffinity, testOnly, theme,
                        uiOptions, vmSafeMode):
        application_set = {'allowTaskReparenting': allowTaskReparenting,
                           'allowBackup': allowBackup,
                           'backupAgent': backupAgent,
                           'debuggable': debuggable,
                           'description': description,
                           'enabled': enabled, 'hasCode': hasCode,
                           'hardwareAccelerated': hardwareAccelerated,
                           'icon': icon, 'killAfterRestore': killAfterRestore,
                           'label': label, 'logo': logo,
                           'manageSpaceActivity': manageSpaceActivity,
                           'largeHeap': largeHeap, 'name': name,
                           'permission': permission, 'persistent': persistent,
                           'process': process,
                           'restoreAnyVersion': restoreAnyVersion,
                           'requiredAccountType': requiredAccountType,
                           'restrictedAccountType': restrictedAccountType,
                           'supportsRtl': supportsRtl,
                           'taskAffinity': taskAffinity, 'testOnly': testOnly,
                           'theme': theme, 'uiOptions': uiOptions,
                           'vmSafeMode': vmSafeMode}
        self.application = application_set

    def set_activity(self, allowTaskReparenting, alwaysRetainTaskState,
                     clearTaskOnLaunch, configChanges, enabled,
                     excludeFromRecents,
                     exported, finishOnTaskLaunch, hardwareAccelerated, icon,
                     label,
                     launchMode, multiprocess, name, noHistory,
                     parentActivityName,
                     permission, process, screenOrientation, stateNotNeeded,
                     taskAffinity,
                     theme, uiOptions, windowSoftInputMode, intentFilter,
                     metaData):
        activity_set = {'allowTaskReparenting': allowTaskReparenting,
                        'alwaysRetainTaskState': alwaysRetainTaskState,
                        'clearTaskOnLaunch': clearTaskOnLaunch,
                        'configChanges': configChanges, 'enabled': enabled,
                        'excludeFromRecents': excludeFromRecents,
                        'exported': exported,
                        'finishOnTaskLaunch': finishOnTaskLaunch,
                        'hardwareAccelerated': hardwareAccelerated,
                        'icon': icon,
                        'label': label, 'launchMode': launchMode,
                        'multiprocess': multiprocess, 'name': name,
                        'noHistory': noHistory,
                        'parentActivityName': parentActivityName,
                        'permission': permission, 'process': process,
                        'screenOrientation': screenOrientation,
                        'stateNotNeeded': stateNotNeeded,
                        'taskAffinity': taskAffinity, 'theme': theme,
                        'uiOptions': uiOptions,
                        'windowSoftInputMode': windowSoftInputMode}
        inner_set = {'activity': activity_set, 'intentFilter': intentFilter,
                     'metaData': metaData}
        self.activities.append(inner_set)

    def set_activity_alias(self, enabled, exported, icon, label, name,
                           permission, targetActivity,
                           intentFilter, metaData):
        activity_alias_set = {'enabled': enabled, 'exported': exported,
                              'icon': icon, 'label': label,
                              'name': name, 'permission': permission,
                              'targetActivity': targetActivity}
        inner_set = {'activity-alias': activity_alias_set,
                     'intentFilter': intentFilter, 'metaData': metaData}
        self.activities_aliases.append(inner_set)

    def set_service(self, enabled, exported, icon, isolatedProcess, label,
                    name, permission,
                    process, intentFilter, metaData):
        service_set = {'enabled': enabled, 'exported': exported, 'icon': icon,
                       'isolatedProcess': isolatedProcess,
                       'label': label, 'name': name, 'permission': permission,
                       'process': process}
        inner_set = {'service': service_set, 'intentFilter': intentFilter,
                     'metaData': metaData}
        self.services.append(inner_set)

    def set_receiver(self, enabled, exported, icon, label, name, permission,
                     process, intentFilter, metaData):
        receiver_set = {'enabled': enabled, 'exported': exported, 'icon': icon,
                        'label': label, 'name': name,
                        'permission': permission, 'process': process}
        inner_set = {'receiver': receiver_set, 'intentFilter': intentFilter,
                     'metaData': metaData}
        self.receivers.append(inner_set)

    def set_provider(self, authorities, enabled, exported, grantUriPermissions,
                     icon, initOrder, label,
                     multiprocess, name, permission, process, readPermission,
                     syncable, writePermission,
                     metaData, grant_uri_permission, path_permission):
        provider_set = {'authorities': authorities, 'enabled': enabled,
                        'exported': exported,
                        'grantUriPermissions': grantUriPermissions,
                        'icon': icon, 'initOrder': initOrder,
                        'label': label,
                        'multiprocess': multiprocess, 'name': name,
                        'permission': permission, 'process': process,
                        'readPermission': readPermission, 'syncable': syncable,
                        'writePermission': writePermission}
        inner_set = {'provider': provider_set, 'metaData': metaData,
                     'grant-uri-permission': grant_uri_permission,
                     'path_permission': path_permission}
        self.providers.append(inner_set)

    def set_application_meta_data(self, meta_data_list):
        self.meta_data = meta_data_list

    def set_uses_library(self, name, required):
        library_set = {'name': name, 'required': required}
        self.uses_libraries.append(library_set)

    def __str__(self):
        return 'package: ' + self.package + ' permissions: ' + ', '.join(
            [str(x) for x in self.uses_permissions])
