# Style Guide {: #style }

Writing style guide to help creating consistent documentation.

This style guide is useful as a reference when reviewing pull-requests for documentation.

!!! abstract "Reference"

    -   [GeoServer Style Guide](https://docs.geoserver.org/latest/en/docguide/style.html)
    -   [GeoNetwork Style Guide](https://docs.geonetwork-opensource.org/4.4/devel/docs/style/)

## Content conventions

### Be concise

Documentation should be concise and not just a brain dump. Reference material should contain short pages and be easy to refer to without having to scroll through a large volume of text. Tutorials can be longer, depending on scope. If the point of the document is to share your thoughts and insights, it belongs in a blog post. This documentation is a manual, not a wiki.

### Avoid marketing

If the point of the document is to showcase a new feature it does not belong in the documentation. Write an article or a blog post about it. If it is necessary to point out a technical benefit of a feature then do so from a technical standpoint.

Bad

> Sub-Portals are a great way to provide a team with their own catalogue!

Good

> Sub-Portals define a distinct catalogue for use.

### Be professional

Avoid the use of slang or other "colorful" language. The point of a technical document is to be informative, not to keep the reader amused. Avoiding slang helps keep the document accessible to as large an audience as possible.

Bad

> 2.  Next, fire up whatever tool you use to browse the web and point it in the direction of \...

Good

> 2.  Next, start your web browser and navigate to \...

### Use direct commands

When providing step-by-step instructions, number steps and use direct commands or requests. Avoid the use of "we" and "let's".

Bad

> Now let's select a record by \...

Good

> 1.  Select a record by \...

## Naming conventions

!!! abstract "Reference"

    -   [Wikipedia naming conventions](https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions)

### Capitalization of page names

Each word in the page name should be capitalized except for articles (such as "the", "a", "an") and conjunctions (such as "and", "but", "or"). A page name should never start with an article.

Bad

> Adding a wms or wfs service

Good

> Adding a WMS or WFS service

Bad

> The Harvester Tutorial

Good

> Harvester Tutorial

### Capitalization of section names

Do not capitalize second and subsequent words unless the title is almost always capitalized in English (like proper names). Thus, capitalize John Wayne and Art Nouveau, but not Video Games.

Bad

> Creating a New Record

Good

> Creating a new record

### Verb usage

It is recommended that the gerund (the -ing form in English) be used unless there is a more common noun form. For example, an article on swimming is better than one on swim.

Bad

> Create a new datastore

Good

> Creating a new datastore

### Avoid plurals

Create page titles that are in the singular. Exceptions to this are nouns that are always plural (scissors, trousers), a small class that requires a plural (polar coordinates, Bantu languages, The Beatles).

Bad

> templates tutorial

Good

> Template tutorial

## Formatting

### Code and command line

Any code or command line snippets should be formatted as code:

``` json
{
   "code": "This is a code block."
}
```

When lines are longer than 80 characters, extend multiple lines in a format appropriate for the language in use. If possible, snippets should be functional when pasted directly into the appropriate target.

For example, XML make no distinction between a single space and multiple spaces, so the following snippets are fine:

``` xml
<namespace:tagname attributename="attributevalue" attribute2="attributevalue"
   nextattribute="this is on another line"/>
```

For shell scripts, new lines can be escaped with a backslash character ([]{.title-ref}).

``` bash
mvn clean install \
    -DskipTests
```

    BUILD SUCCESS

It is helpful to separate out input from output, so that the command can be easily copied as shown above.
