/**
 * Glue code to provide Growl-like notifications.
 * @author Pavlo Kapyshin (i@93z.org)
 * @copyright Original Coding (http://originalcoding.com/)
 * @version 0.2.2
 * License: BSD, see http://github.com/originalcoding/growl.js/blob/master/LICENSE
 */


/**
 * Growl class.
 * @constructor
 * @param {Object} settings Growl settings
 */
Growl = function (settings) {
    /**
     * Settings that Growl makes use of:
     *     element Growl element.
     *     types {Object} Object that holds settings for notification types.
     *                    Example:
     *                        {
     *                            error: {
     *                                sticky: true
     *                            },
     *
     *                            success: {
     *                                sticky: false,
     *                                timeout: 5000
     *                            }
     *                        }
     *     bind {Boolean} Should Growl bind methods for types (for example, Growl.success)?
     *     add {Function} Function responsible for adding message to the Growl element.
     *                    Example:
     *                        function (growlElement, notification, settings) {
     *                            // Formatting notification according to settings,
     *                            // adding notification element to growlElement
     *                            // and assigning it to variable named notificationElement.
     *                            return notificationElement;
     *                        };
     *     remove {Function} Function responsible for removing message element from Growl element.
     *                       Example:
     *                           function (growlElement, notificationElement, settings) {
     *                               // Removing notificationElement which is a value returned
     *                               // by 'add' function.
     *                           }
     *     timeout {Number} Timeout for notifications in milliseconds.
     *     sticky {Boolean} Are notifications sticky?
     *
     * You can provide your own settings.
     */
    var settings = settings || {};

    var types = settings.types = settings.types || {};
    var bind = settings.bind = ('bind' in settings) ? settings.bind : true;

    this.settings = settings;


    var hasOwnProperty = function(obj, prop) {
        if (Object.prototype.hasOwnProperty) {
            return obj.hasOwnProperty(prop);
        };

        return typeof obj[prop] != 'undefined' &&
               obj.constructor.prototype[prop] !== obj[prop];
    };

    var mergeSettings = function () {
        var mergedObject = {};

        for (var i = 0, length = arguments.length; i < length; i++) {
            var object = arguments[i];

            for (var prop in object) {
                if (hasOwnProperty(object, prop)) {
                    mergedObject[prop] = object[prop];
                };
            };
        };

        delete mergedObject.types;
        return mergedObject;
    };


    /**
     * Adds notification.
     * @this {Growl}
     * @param notification Notification (can be anything)
     * @param {Object} notificationSettings Settings for notification
     * @return Result of 'add' function defined in settings
     */
    this.addNotification = function (notification, notificationSettings) {
        var notificationSettings = notificationSettings || {};

        var notificationType = notificationSettings.type;
        var typeSettings = this.settings.types[notificationType] || {};

        var settings = mergeSettings(this.settings, typeSettings, notificationSettings);

        var growlElement = settings.element;
        var notificationElement = settings.add(growlElement, notification, settings);

        if (settings.sticky !== true) {
            var remove = function () {
                settings.remove(growlElement, notificationElement, settings);
            };
            setTimeout(remove, settings.timeout);
        };

        return notificationElement;
    };


    /**
     * Adds new message type and modifies its settings. If 'bind' setting is true,
     * binds return value to Growl object (for example, Growl.warning).
     * @this {Growl}
     * @param {String} typeName Type's name
     * @param {Object} typeSettings Settings for type
     * @return {Function} Function that adds notifications for defined type.
     */
    this.addType = function (typeName, typeSettings) {
        var types = this.settings.types;

        // merge old type's settings and the new ones
        types[typeName] = mergeSettings(types[typeName] || {}, typeSettings || {});

        var that = this;
        var typeMethod = function (notification, notificationSettings) {
            var notificationSettings = notificationSettings || {};
            notificationSettings.type = typeName;
            return that.addNotification(notification, notificationSettings);
        };

        if (this.settings.bind) {
            this[typeName] = typeMethod;
        };

        return typeMethod;
    };


    /**
     * Removes type by name.
     * @this {Growl}
     * @param {String} typeName Type's name
     */
    this.removeType = function (typeName) {
        delete this[typeName];
        delete this.settings.types[typeName];
    };


    if (bind) {
        for (var type in types) {
            if (hasOwnProperty(types, type)) {
                this.addType(type, types[type]);
            };
        };
    };
};

