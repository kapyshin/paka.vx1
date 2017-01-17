In 2010 I created [small JavaScript library](https://github.com/originalcoding/growl.js)
for in-browser “notifications”. Though its API was documented, no tutorial was written.
Actually, this is not surprising, as growl.js is unpopular even at Original Coding:
it was used in several projects, and then focus shifted to projects where work is 90%
backend. But I wouldn’t be writing this just to say that, right? I prepared short
introduction to library, just in case you need to understand how to use it. But it’s
still better to use something modern, e.g. some [React](http://facebook.github.io/react/)
component.

First of all, there is a [complete demo](demo/)—check it out. Basically, it contains
two “panels” (green and red): each has text input and button. You type some text into
input, press button, and new notification is added. Each notification type has its own
settings that define its behaviour. Two types of notifications are defined in demo:
`success` and `error`. “Success” notifications are shown for 5 seconds, and then disappear.
“Error” ones stay on page until you “close” them. Now let’s look at the code.

At the bottom of <a href="demo/main.js"><code>main.js</code></a> there is following:

```
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
```

As you can see, new instance of `Growl` class is created and some options
(growl.js calls them “settings”) are passed:

<dl>
  <dt><code>element</code></dt>
  <dd>This is container for all notifications. It can be <code>HTMLElement</code> (like in demo), jQuery-wrapped <code>HTMLElement</code>, or anything else.</dd>
  <dt><code>types</code></dt>
  <dd>Each notification has type (e.g. <code>success</code>), and this is where you define both types and their settings. <code>sticky</code> notifications are not removed automatically. Non-<code>sticky</code> notifications are removed after <code>timeout</code> (in milliseconds) is passed (removal is done by call to <code>remove</code> function which is described below).</dd>
  <dt><code>add</code></dt>
  <dd>This is a function that accepts <code>element</code>, notification message (which in demo is taken from text input’s <code>value</code>), and settings (so you can get type of notification via <code>settings.type</code>); it returns notification element (anything you want, as <em>you</em> handle it in <code>remove</code>) that will be passed to <code>remove</code>. It does what you make it to do: in demo I create new <code>div</code>, add classes, set its <code>innerHTML</code>, and add to <code>element</code>. For <code>sticky</code> notifications I also create <code>span</code> with <code>click</code> handler that removes notification element from <code>element</code>.</dd>
  <dt><code>remove</code></dt>
  <dd>This is a function that accepts <code>element</code>, notification element (whatever you returned from <code>add</code>), and settings; it doesn’t return anything. It does what you make it to do: in demo I remove notification element from <code>element</code> (and if after that <code>element</code> contains no notification elements, the former is hidden).</dd>
  <dt><code>bind</code></dt>
  <dd>
    <p>If <code>bind</code> is <code>true</code>, growl.js adds shortcuts for <code>addNotification</code> method, so notifications could be added via <code>growl[type of notification]("Hello!", extra settings)</code>.</p>
    <p>Look at code from demo:</p>
<pre><code>growl.success("Page is loaded.", {timeout: 1000});</code></pre>
    <p>This is equivalent to following:</p>
<pre><code>growl.addNotification("Page is loaded.", {type: "success", timeout: 1000});</code></pre>
  </dd>
</dl>

After `Growl` instance is created, you can use it to add notifications
with shortcuts (e.g. `growl.error("Put the cookie down!")`) or
with `addNotification` (like I do in `setUpPanel` function in `main.js`):

```
var val = messageInputEl.value.trim();
if (val) {
    growl.addNotification(val, {type: type});  // type is string, like "error" or "success"
}
```

And that’s it. For “how it may look” look at the [demo](demo/), for “how it’s done”
see <a href="demo/main.js"><code>main.js</code></a>.
