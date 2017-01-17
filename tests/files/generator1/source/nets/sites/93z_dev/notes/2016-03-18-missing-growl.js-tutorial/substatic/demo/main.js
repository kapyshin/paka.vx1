;(function () {
    var show = function (el) {
        el.style.display = "block";
    };
    var hide = function (el) {
        el.style.display = "none";
    };
    var $ = function (id) {
        return document.getElementById(id);
    };
    var on = function (target, eventName, callback) {
        target.addEventListener(eventName, callback, false);
    };
    var isEnter = function (evt) {
        return (
            evt.which === 13 || evt.keyCode === 13 ||
            evt.code === "Enter" || evt.key === "Enter");
    };
    var setUpPanel = function (type, growl) {
        var panelEl = $(type + "-panel");
        var messageInputEl = panelEl.querySelector(".message-input"),
            triggerEl = panelEl.querySelector(".trigger");
        var addMessage = function () {
            var val = messageInputEl.value.trim();
            if (val) {
                growl.addNotification(val, {type: type});
                messageInputEl.value = "";
            } else {
                growl.error(
                    "Oops. Nothing to show.", {sticky: false, timeout: 1000});
                messageInputEl.focus();
            }
        }
        on(triggerEl, "click", addMessage);
        on(messageInputEl, "keyup", function (evt) {
            if (isEnter(evt)) {
                addMessage();
            }
        });
        return messageInputEl;
    };
    var addGrowlMessage = function (growlEl, notification, settings) {
        // Create notificationEl with classes and contents.
        var notificationEl = document.createElement("div");
        notificationEl.classList.add("message");
        notificationEl.classList.add(settings.type);
        notificationEl.innerHTML = notification;
        // Add closing "button" if this is sticky notification.
        if (settings.sticky) {
            var closeEl = document.createElement("span");
            closeEl.classList.add("message-close-trigger");
            closeEl.textContent = "×";  // yes, this is multiplication sign :)
            on(closeEl, "click", function () {
                settings.remove(growlEl, notificationEl, settings);
            });
            notificationEl.appendChild(closeEl);
        }
        // Add notificationEl to growl.
        growlEl.appendChild(notificationEl);
        show(growlEl);
        return notificationEl;
    };
    var removeGrowlMessage = function (growlEl, notificationEl, settings) {
        growlEl.removeChild(notificationEl);
        if (growlEl.children.length < 1) {
            hide(growlEl);
        }
    };
    on(window, "DOMContentLoaded", function () {
        // Initialize growl element.
        var growlEl = document.createElement("div");
        growlEl.setAttribute("id", "growl");
        hide(growlEl);
        document.body.appendChild(growlEl);
        // Initialize growl.
        var growl = new Growl({
            element: growlEl,
            types: {
                error: {sticky: true},
                success: {sticky: false, timeout: 5000}
            },
            bind: true,
            add: addGrowlMessage,
            remove: removeGrowlMessage
        });
        // Set up controls for sending notifications.
        setUpPanel("success", growl);
        setUpPanel("error", growl).focus();
        growl.success("Page is loaded.", {timeout: 1000});
    });
})();
