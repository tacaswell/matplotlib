.. _explain-threads:

Matplotlib and thread safety
============================

The answer to "Is Matplotlib thread safe" is "it depends".  Matplotlib's
extensions modules are thread-safe in the sense of "we will not segfault
Python", but Matplotlib was not built with threads in mind and is not
generically thread-safe.  However, it is possible to safely use a sub-set of
Matplotlib with threads.

Things that are thread un-safe
------------------------------

GUI toolkits tend to expect their main loop to be run on the main thread and
may or may not be able to deal with GUI objects created in on thread being used
in other threads.  This is a constrained placed on us by the GUI toolkits and
not something we can work around.

The implicit API is built around the (global) shared state of "current Figure"
and "current Axes" to control where the plotting commands are directed.  This
make `.pyplot` nearly impossible to use reliable with threads.  For example,

.. code-block:: python

   import threading

   import matplotlib.pyplot as plt
   plt.switch_backend('agg')

   def bad_idea(n):
       plt.figure()
       plt.plot(range(5), [n] * 5)
       plt.savefig(f'plot_{n}.png')

   threads = [threading.Thread(target=bad_idea, args=(j,)) for j in range(5)]
   [t.start() for t in threads]
   [t.join() for t in threads]

will run without error, but exactly what it will save is not well defined!  If
you are working with threads we strongly advise you do not use the implicit
(pyplot) API.

Things that are safe-ish
------------------------

Another place in Matplotlib where we have shared state is `.rcParams`. However,
Matplotlib does not internally write to the ``rcParams`` during normal
operations.  The two exceptions are :rc:`backend` which is used by ``pyplot``
while setting the GUI backend to use and :rc:`savefig.directory` which is set
from GUI file selectors.  In both cases, if either code path were run not on
the main thread there are likely to be other problems than race conditions.

Things that are safe
--------------------

So long as `.figure.Figure` objects are only worked on by one thread at a
time, it is safe to generate and save figures from multiple threads:

.. code-block:: python

   from matplotlib.figure import Figure
   import numpy as np

   M = 30
   N = 500
   no_text = False
   th = np.linspace(0, 2*np.pi)

   def good_idea(rank, barrier):
       barrier.wait()
       for j in range(N):
           fig = Figure()
           ax = fig.subplots()
           ax.set_ylim(-1.1, 1.1)
           ax.set_xlim(0, np.pi*2)
           ax.plot(th, np.sin(th + 2*np.pi * j / N))
           # There is a global lock on rendering text
           if no_text:
               ax.axis('off')
           fig.savefig(f'/tmp/threads_{rank:02d}_{j:03d}.png')


   barrier = threading.Barrier(M)
   threads = [threading.Thread(target=good_idea, args=(j, barrier,)) for j in range(M)]
   [t.start() for t in threads]
   [t.join() for t in threads]

There is currently a global lock on freetype so that only one string can be
rendered at a time.  In many real-world figures the text rendering will be the
limiting factor (text rendering is surprisingly expensive), however if in other
cases the per-figure creating and rendering time is dominated by other processes —
such as data preparation or image resampling and color mapping — it may be worth
parallelizing image generation.
