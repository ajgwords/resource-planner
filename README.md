# resource-planner
Helps look at upcoming availability and projects and work out whether there are enough days in your life!

# Use
* Clone repo or just download the script
* Create or download the projects.yaml file
* On Linux use `chmod +x rp.py` to make the file executable and run the script using `./rp.py -f projects.yaml` or 
* Use `python rp.py -f projects.yaml`
  * NOTE: MUST provide the path to your YAML file using the -f or --file argument:
* 
# yaml file
Ensure that `pyyaml` is installed in the correct location

Requires 3 sections:
* settings - general tool settings
  * include the number of days you work per week, and whether you want to mix projects or complete them in blocks
* projects - details about each project 
  * add in information including a name, start and end dates, the number of days allocated or quoted for completion of the work and the priority of the project (e.g. 1 would be a project that is live and needs to be completed soonest and then other priorities could be less urgent live projects or quoted work in an order of preference)
* holidays - dates of working days that are assigned as holidays
  * need to include national holidays here