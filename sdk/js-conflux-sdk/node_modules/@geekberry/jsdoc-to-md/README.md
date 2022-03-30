
# Jsdoc to Markdown

# Install
`npm install @geekberry/jsdoc-to-md`

# Document

## jsdocToMd <a id="index.js/jsdocToMd"></a>

Generate directory markdown string.

* **Parameters**

Name            | Type       | Required | Default  | Description
----------------|------------|----------|----------|-----------------------------
path            | `string`   | true     |          | - Filename or directory path
options         | `object`   | false    |          |
options.content | `boolean`  | false    | true     | Generate content.
options.filter  | `function` | false    | ()=>true | Filename filter/

* **Returns**

`string` Markdown string

* **Examples**

```
> const jsdocToMd = require('@geekberry/jsdoc-to-md')
> const string = jsdocToMd('./src')
```

# Example

[see](https://github.com/GeekBerry/jsdoc-to-md/blob/master/example)
