"""
The MIT License (MIT)
Copyright © 2018 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

import _thread

class MicroWorkers :

    # ============================================================================
    # ===( Thread )===============================================================
    # ============================================================================

    def _workerThreadFunc(self, arg) :
        threadID = _thread.get_ident()
        print('[THREAD %s] - Starts' % threadID)
        while(True) :
            self._workersLock.acquire()
            try :
                job = self._jobs.pop(0)
            except :
                job = None
                self._workersLock.acquire()
            self._workersLock.release()
            if job :
                jobName   = job['name']
                jobFunc   = job['func']
                jobArg    = job['arg']
                jobCBFunc = job['cbFunc']
                print('[THREAD %s] - Starts job %s' % (threadID, jobName))
                try :
                    jobResult = jobFunc(jobName, jobArg)
                    print('[THREAD %s] - End of job %s' % (threadID, jobName))
                except Exception as ex :
                    jobResult = None
                    print( "[THREAD %s] - Exception in job %s: %s"
                           % ( threadID, jobName, ex ) )
                if jobCBFunc :
                    try :
                        jobCBFunc(jobName, jobArg, jobResult)
                    except Exception as ex :
                        print( "[THREAD %s] - Exception in callback after end of job %s: %s"
                               % ( threadID, jobName, ex ) )

    # ============================================================================
    # ===( Constructor )==========================================================
    # ============================================================================

    def __init__(self, workersCount, workersStackSize=0) :
        if workersStackSize > 0 and workersStackSize < 4096 :
            workersStackSize = 4096
        self._workersCount = workersCount
        self._workersLock  = _thread.allocate_lock()
        self._jobs         = [ ]
        if workersCount > 0 :
            originalStackSize = _thread.stack_size()
            _thread.stack_size(workersStackSize)
            print('Create a pool of %s thread(s) :' % workersCount)
            for x in range(workersCount) :
                _thread.start_new_thread(self._workerThreadFunc, (None, ))
            _thread.stack_size(originalStackSize)

    # ============================================================================
    # ===( Functions )============================================================
    # ============================================================================

    def AddJob(self, name, function, arg=None, onFinished=None) :
        self._jobs.append( { 'name'   : name,
                             'func'   : function,
                             'arg'    : arg,
                             'cbFunc' : onFinished } )
        self._workersLock.release()

    # ----------------------------------------------------------------------------

    def Count(self) :
        return self._workersCount

    # ============================================================================
    # ============================================================================
    # ============================================================================