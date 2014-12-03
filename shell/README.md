# appsrepo-shell
This is an interactive shell to query the collection of apps using a Domain Specfic Language (DSL).

##Usage
To start the interactive shell, simply run: ``` python shell.py ```
You may need to edit the configuration file, ```config/appsrepo-shell.conf```, to change default settings.

## Domain Specific Language (DSL)
The basic syntax is: 

**```(package_name)[index].feature.function()```**

The syntax is explianed below:

- (package_name) - The package name to find a specific app.
- [index] - An index that corresponds to the order of the app version.
- feature - A feature of the app (e.g., permissions, layouts, Button, etc.)
- function() - A function to perform a specfic action on the feature of the app (e.g., count(), max(), min(), diff(), etc).

### Syntax
#### Selecting Apps
- Use the package name to select a particular app.
  - Example: ```(com.mobile.app).action()```
- Use the __*__ wildcard to select unknown apps.
  - Example: ```(*).action()```
 - Package names or wild cards are always emebeded in paranthesis.

#### Predicates: Selecting Versions
Predicates are used to select a particular version. Apps are indexed by the order of their versions with the first version having index 0 and the last version having index -1. Predicates are optional and always embedded in square brackets.

| Predicate |   Description     |
| ------------- |:-------------:|
| * | Matches all app's versions |
| [0] | Matches the first version |
| [-1] | Matches the last version |
| [3] | Matches the first four versions |
| [-2] | Matches the last two versions |

## Examples:
- Find all the requested permissions for the first version of the evernote app:
  - ```(com.evernote)[0].permissions.find()```
- Find all the requested permissions for the first three version of evernote app:
  - ```(com.evernote)[2].permissions.find()```
- Find all the requested permissions for the evernote app:
  - ```(com.evernote)[].permissions.find()```
- Find the number of requested permissions for the last version of the evernote app:
  - ```(com.evernote)[].permissions.count()```