# Documentation

The following is an extract of all functionality offered by `sspm`. Please use `sspm --help` or `sspm <action> --help` to access the complete command-line help. 

## Initialization

Before `sspm` can be used to manage projects, it must be initialized:

```bash
> sspm init
Initializing sspm
Please specify `project.location` = E:\Projects
Project folder `E:\Projects` does not exist. Create [Y|n]? y
Projects folder `E:\Projects` successfully created.
Updating `project.location` in configuration file.

sspm initialized. Run `sspm config show` to visualize current configuration.
```

## Getting help

Help can be obtained as follows:

```bash
> sspm --help
Usage: sspm [OPTIONS] COMMAND [ARGS]...

Commands:
  config   Manage configuration options.
  init     Initialize.
  project  Manage projects.
  stats    Collect statistics.
  version  Print version information.
```

The various commands have their own help:

```bash
> sspm config --help
Usage: sspm config [OPTIONS] COMMAND [ARGS]...

  Manage configuration options.

Options:
  --help  Show this message and exit.

Commands:
  get       Get the value of the option with specified key.
  keys      Show the list of valid configuration keys.
  location  Show full path of configuration file.
  set       Set the option with specified name to the passed value.
  show      Show current configuration options.
```

## Configuration

All `config` actions can be listed with:

```bash
> sspm config --help
Usage: sspm config [OPTIONS] COMMAND [ARGS]...

  Manage configuration options.

Options:
  --help  Show this message and exit.

Commands:
  get       Get the value of the option with specified key.
  keys      Show the list of valid configuration keys.
  location  Show full path of configuration file.
  set       Set the option with specified name to the passed value.
  show      Show current configuration options.
```

Current configuration can be displayed with:

```bash
$ sspm config show
Current configuration:
projects.location = E:/Projects
projects.external_data =
tools.git_path =
tools.use_git = True
tools.git_ignore_data = True

Use `sspm config set <key> <value>` to change configuration.
Use `sspm config keys` to show the list of valid config keys.
```

Explanation of the configuration keys:

| Configuration key        | Explanation                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `projects.location`      | Root project folder.                                         |
| `projects.external_data` | (Optional, leave blank to ignore). External location of project data (*e.g.*, a larger store). Projects also have a sub-folder `data`. See Projects session below. |
| `tools.git_path`         | Full path to git executable. Omit if `git` is in the system path or if git is not used (see `tools.use_git`) |
| `tools.use_git`          | Boolean (`True` or `False`) to enable/disable initializing newly created Projects as `git` repositories. |
| `tools.git_ignore_data`  | Boolean (`True` or `False`) to toggle adding the `data` folder to `.gitignore`. |

Setting a configuration key-value pair can be done as follows:

```bash
> spm config set projects.external_data N:\External_Data
```

## Projects

A complete list of project actions can be obtained with:

```bash
> sspm project --help
Usage: sspm project [OPTIONS] COMMAND [ARGS]...

  Manage projects.

Options:
  --help  Show this message and exit.

Commands:
  close   Close the requested project either "now" or at the date of the "latest" modification.
  create  Create a new project.
  get     Get value for the requested metadata key of given project.
  keys    Return a list of editable keys for the projects.
  list    List all projects.
  open    Open a requested or all projects folder in the system's file explorer.
  set     Set value for the specified metadata key of given project.
```

A project can be created in interactive way:

```bash
> sspm project create
[*] Project title: My first project
[*] User's first and family name: John Doe
[*] User's e-mail address: john.doe@example.com
[*] User's (scientific) group: My Group
[ ] Short description for the project: This demo project shows hows to use `sspm`.
Initialized empty Git repository in E:/Projects/2022/10/P_0000/.git/
[master (root-commit) 841e6ff] "Initial import."
 3 files changed, 19 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 metadata/description.md
 create mode 100644 metadata/metadata.ini
Success! Project 'E:\Projects\2022\10\P_0000' was created and initialized.
```

Alternatively, the same information can be passed as command-line arguments. See `sspm project create --help` for details.

Current projects can be visualized with:

```bash
> sspm project list
╒════════╤══════════════════╤═════════════╤══════════╤══════════╕
│ ID     │ Title            │ User name   │ Group    │ Status   │
╞════════╪══════════════════╪═════════════╪══════════╪══════════╡
│ P_0000 │ My first project │ John Doe    │ My Group │ new      │
╘════════╧══════════════════╧═════════════╧══════════╧══════════╛
```

or, with more details:

```
> sspm project list --detailed
╒════════╤═════════╤════════╤═══════ ... ╤═════════════╤═════════════╤══════════════╤════════════╤══════════╕
│   Year │   Month │ ID     │ Title  ... │ User name   │ Group       │ Start date   │ End date   │ Status   │
╞════════╪═════════╪════════╪═══════ ... ══════════════╪═════════════╪══════════════╪════════════╪══════════╡
│   2022 │      10 │ P_0000 │ My fir ... │ John Doe    │ My Group    │ 31/10/2022   │            │ new      │
╘════════╧═════════╧════════╧═══════ ... ╧═════════════╧═════════════╧══════════════╧════════════╧══════════╛
```

The structure of the newly created project can be inspected in the system file explorer with:

```bash
> sspm project open P_0000
```

Project key-value pairs can be set with:

```bash
> sspm project P_0000 set status "in progress"
```

The list of valid keys can be obtained with:

```bash
> sspm project keys
Valid editable project keys are: ['project.title', 'user.name', 'user.email', 'user.group', 'project.start_date', 'project.end_date', 'project.status']
```

A project can be closed by manually setting `project.end_date` and `projects.status`, or by using `sspm project close <project_ID> now|latest`. When closing `now`, today's date will be used as `project.end_date`; with `latest`, the date of the last file modification found in the project folder will be used instead. The `project.status` will be set to `completed`.

```bash
> sspm project close P_0000 latest
Project closed with end date 31/10/2022.
```

## Statistics

The statistics module is still very simple. Total number of projects grouped by year and group are returned.

```bash
> sspm stats show
╒════════╤═════════════╤════════════╕
│   Year │ Group       │   Projects │
╞════════╪═════════════╪════════════╡
│   2022 │ My Group    │          1 │
╘════════╧═════════════╧════════════╛
```

More functionality will be added in future releases.