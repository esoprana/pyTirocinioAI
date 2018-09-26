.. pyTirocinioAI documentation master file, created by
   sphinx-quickstart on Fri Sep  7 15:43:27 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyTirocinioAI's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. image:: https://travis-ci.org/esoprana/pyTirocinioAI.svg?branch=master
    :target: https://travis-ci.org/esoprana/pyTirocinioAI

.. image:: https://api.codacy.com/project/badge/Coverage/9156448a3fd1471080b292fcea85361b
    :target: https://www.codacy.com/app/esoprana/pyTirocinioAI?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=esoprana/pyTirocinioAI&amp;utm_campaign=Badge_Coverage

.. image:: https://api.codacy.com/project/badge/Grade/9156448a3fd1471080b292fcea85361b
    :target: https://www.codacy.com/app/esoprana/pyTirocinioAI?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=esoprana/pyTirocinioAI&amp;utm_campaign=Badge_Grade

.. image:: https://travis-ci.org/esoprana/pyTirocinioAI.svg?branch=master
    :target: https://esoprana.github.io/pyTirocinioAI/

Database structure
==================
.. image:: _static/db.svg

Rules structure
===============
This is an example of condition, in onParam and onMsg only "static" condition are permitted, instead in py is possible to use any valid python expression(during the execution of this "_" contains the list of Params and "m" contains all the information about the user message.


.. code-block:: javascript
   :linenos:

    {
        "onParam": [
            {
                "w__ne": "k"
            },
            {
                "d__ne": "prova",
                "c__eq": "ciao",
                "test1" : {
                    "a__lt": 1
                    "b__ge": 2
                    "k__in": [1,2,3,4]
                },

                "__has__": ["c"]
                "__type__": <topic_id>
            }
        ],
        "onMsg": {
            "intent": {
                "name__in": [<intent_name>, <intent_name2>]
            }
        }
        "py" : "_[0].values['k']!=_[1].values['d'] && _[0].priority < _[1].priority"
    }

onMsg and onParam use the same type of schema to impose conditions.
If an object is None all conditions are evaluated to true, to check that an object is not none is possible to use "__has__".
"__type__" is evalueted to true only when the Params to which is evaluated against has a specified <topic_id>

In action.operations we can then use:

.. code-block:: javascript
    :linenos:

    [
        {
            "op": "exportNames",
            "index": 0,
            "val": <any valid python expression using _ or m>
            "name": "test"
        }, /* Writes in _[0].values['test'] = <result of valid python expression> */
        {
            "op": "exportNames",
            "index": 1,
            "val": None
            "name": "test1"
        }, /* Deletes 'test1' field from _[0].values */
        {
            "op": "popUntil",
            "index": 2
        }, /* Deletes all Params with priority lower than _[2].priority */
        {
            "op": "pop"
        }, /* Deletes Params on top of stack */
        {
            "op": "push",
            "topic": <id_of_topic>
        }, /* Adds topic on top of stack(and last of _) */
    ]

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* `Swagger <_static/swagger.json>`_
* `Swagger ui <http://petstore.swagger.io/?url=https://esoprana.github.io/pyTirocinioAI/_static/swagger.json>`_
