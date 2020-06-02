Reference
=========

Current architecture.

.. graphviz::

   digraph G {

      compound=true;
      subgraph cluster2 {
      label = "CANanalyze";
      node [style=filled, color=grey, shape=component];
      
      subgraph cluster0 {
        label = "ISO stack";
        style=solid;
	color=lightgrey;

	subgraph cluster01 {
          label="Application layer";
	  rankdir=LR;
	  rank=same;
	  data_by_identifier  -> uds;
	  diag_session -> uds;
	  security_access -> uds;
	};

        subgraph cluster02 {
          label="Network layer";
	  isotp;
	};

	subgraph cluster03 {
	  label="Data-link layer";
	  abstract_can -> komodo_can;
	  abstract_can -> python_can;
	};

	subgraph cluster04 {
	  label="Physical layer";
	  komodo;
	};

        uds -> isotp;
	isotp -> abstract_can;
	komodo_can -> komodo;

      };

      subgraph cluster1 {
        label = "Context";
        node [style=filled, color=grey, shape=component];
	tools;
	context;
      };

      isotp -> tools [ltail=cluster0, lhead=cluster1];
      context -> abstract_can;
      };
      
   }

.. Future architecture.
.. 
.. .. graphviz::
.. 
..    digraph {
..       compound=true;
..       subgraph cluster0 {
..         node [style=filled,color=white,shape=polygon,sides=4];
..         style=filled;
..         color=lightgrey;
..         "uds" -> "isotp" -> "can" -> "phy";
.. 	"phy" -> "komodo"
.. 	"phy" -> "socketcan"
..         label = "communication";
..       };
..       subgraph cluster1 {
..         "tools";
.. 	"context";
..       };
..       "isotp" -> "tools" [ltail=cluster0, lhead=cluster1];
..       # "uds" -> "context";
..       # "isotp" -> "context";
..       # "can" -> "context";
..    }

Communication stack
-------------------


routine_control
^^^^^^^^^^^^^^^

.. automodule:: cananalyze.routine_control
   :members:

security_access
^^^^^^^^^^^^^^^
.. automodule:: cananalyze.security_access
   :members:

data_by_identifier
^^^^^^^^^^^^^^^^^^
.. automodule:: cananalyze.data_by_identifier
   :members:

uds
^^^

.. automodule:: cananalyze.uds
   :members:
   
isotp
^^^^^

.. automodule:: cananalyze.isotp
   :members:

abstract_can
^^^^^^^^^^^^

.. automodule:: cananalyze.abstract_can
   :members:

komodo_can
^^^^^^^^^^

.. automodule:: cananalyze.komodo_can
   :members:

python_can
^^^^^^^^^^

.. automodule:: cananalyze.python_can
   :members:

komodo
^^^^^^

.. automodule:: cananalyze.komodo_py
   :members:

Context tools
-------------
   
context
^^^^^^^

.. automodule:: cananalyze.context
   :members:

tools
^^^^^

.. automodule:: cananalyze.tools
   :members:
