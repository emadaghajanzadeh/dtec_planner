
(define (domain d1)
  (:requirements :strips :typing :durative-actions)

  (:predicates 
        (predicate_1)
        (predicate_2)
        (predicate_3)
        (predicate_4)
        (predicate_5)
        (predicate_6)
    )

  (:durative-action action1
   :parameters ()
   :duration (= ?duration 2.5)
   :condition (and  (at start(predicate_1)) (at start(predicate_2)) )
   :effect (and (at end (predicate_4))))


  (:durative-action action2
   :parameters ()
   :duration (= ?duration 2.5)
   :condition (at start (predicate_3))
   :effect (at end (predicate_5)))


  (:durative-action action3
   :parameters ()
   :duration (= ?duration 3)
   :condition (and (at start(predicate_4)) (at start(predicate_5)) )
   :effect (at end (predicate_6)))
    
    )