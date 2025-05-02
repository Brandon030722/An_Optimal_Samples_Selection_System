## **README**
Writen by Zhouzitao



### **Table of Contents**
1. [Overview](#_overview)
1. [](#_overview)[Prerequisites](#_prerequisites)
1. [](#_prerequisites)[Quick Start](#_quick start)
1. [](#_quick start)[Project Layout](#_project layout)
1. [](#_project layout)[FrontEnd WalkThrough](#_front_x001e_end walk_x001e_through)
1. [](#_front_x001e_end walk_x001e_through)[Parameter Reference](#_parameter reference)
1. [](#_parameter reference)[Typical Workflow](#_typical workflow)
1. [](#_typical workflow)[Database (.db) Handling](#_database \(.db\) handling)
1. [](#_database \(.db\) handling)[FAQ](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
[](#_faq)
### [](#_faq)<a name="_overview"></a>**Overview**
**An Optimal SampleSelection System** is a lightweight tool for generating optimal sample groupings.

**Backend**: Flask (server.py) calls main.multi\_round\_greedy()

**Frontend**: singlepage HTML/CSS/JS GUI

**Persistence**: save results as .db files; list / view / delete anytime

-----
### <a name="_prerequisites"></a>**Prerequisites**

|**Tool**|**Version**|**Notes**|
| :-: | :-: | :-: |
|Python|≥ 3.8|required|
|pip|latest|package installer|
|Flask|≥ 2.3|pip install flask flask-cors|
|Browser|modern|Edge / Chrome / Firefox|




-----
### <a name="_quick start"></a>**Quick Start**
git clone <repo-url>

cd <repo>

pip install flask flask-cors

python server.py    **# runs on http://127.0.0.1:8000**

Open the URL above in your browser and you’re ready.

-----
###
### <a name="_project layout"></a>**Project Layout**
project/

├─ server.py       # Flask backend

├─ main.py         # core algorithm (not shown here)

├─ static/

│  └─ index.html   # singlepage frontend

└─ db/             # autocreated storage for .db files

-----
### <a name="_front_x001e_end walk_x001e_through"></a>**FrontEnd WalkThrough**

|**#**|**UI Element**|**Purpose**|
| :-: | :-: | :-: |
|1|**m**|total pool size|
|2|**n**|number of samples to pick|
|3|**Mode**|**Random n** or **Selected n**|
|4|**Selected IDs**|enabled only in *Selected n* mode|
|5|**k / j / s**|algorithm parameters|
|6|**min\_s\_covered**|min coverage per sample|
|7|**max\_trials**|outer loop cap|
|8|**sample\_per\_round**|samples per greedy round|
|9|**Run**|start algorithm (shows progress bar)|
|10|**Store (.db)**|persist result to db/|
|11|**Go to DB**|switch to DB page|
|12|**Clear**|reset to defaults|
|13|**Result**|shows Selected list and Gxx groups|
|14|**DB Page**|list/display/delete/print .db files|


-----
###
###
###
### <a name="_parameter reference"></a>**Parameter Reference**

|**Name**|**Type**|**Default**|**Description**|
| :-: | :-: | :-: | :-: |
|m|int|45|size of full sample pool|
|n|int|10|number of samples to choose|
|Mode|radio|Random|selection mode|
|selected|list[int]|–|explicit IDs in *Selected* mode|
|k|int|6|items per group|
|j|int|4|overlap constraint|
|s|int|4|target cooccurrence|
|min\_s\_covered|int|1|min coverage per item|
|max\_trials|int|50|outer loop iterations|
|sample\_per\_round|int|200|candidates per round|

**Tooltips ( ? ) provide English hints.**

-----

### <a name="_typical workflow"></a>**Typical Workflow**
1. Fill **m, n, k, …**
1. Choose **Selected n** and enter IDs  (**if needed)**
1. Click **Run** – watch the blue progress bar
1. If satisfied, click **Store (.db)**
1. Switch to **DB Page** → *Display* or *Delete* files or print (**if needed)**

-----

### <a name="_database (.db) handling"></a>**Database (.db) Handling**
Files live in db/ with pattern m-n-k-j-s-idx-groups.db

Copy files to other systems for further analysis if you like

-----
### <a name="_faq"></a>**FAQ**

|**Question**|**Fix**|
| :-: | :-: |
|**Run button seems dead**|<p>1) backend not running</p><p>2) bad parameters (check browser console)</p>|
|**CORS errors**|open via 127.0.0.1:8000, not file://|
|**Cannot write .db**|ensure db/ exists and is writable|

-----

