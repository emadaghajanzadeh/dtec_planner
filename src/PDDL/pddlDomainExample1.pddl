; Source: https://www.cs.toronto.edu/~sheila/384/w11/Assignments/A3/veloso-PDDL_by_Example.pdf

; On differences of different PDDL's versions
(define (domain d1)
  (:requirements :strips :typing :durative-actions)

  (:predicates (room ?r)  (ball ?b) (gripper ?g) (at-robby ?r)
               (at ?b ?r) (free ?g) (carry ?o ?g))

  (:durative-action move
   :parameters (?from ?to)
   :duration (= ?duration 3)
   :condition (and  (room ?from) (room ?to) (at-robby ?from))
   :effect (and (at-robby ?to) (not (at-robby ?from))))


  (:durative-action pick
   :parameters (?obj ?room ?gripper)
   :duration (= ?duration 3)
   :condition (and (ball ?obj) (room ?room) (gripper ?gripper)
                      (at ?obj ?room) (at-robby ?room) (free ?gripper))
   :effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper))))


  (:durative-action drop
   :parameters (?obj ?room ?gripper)
   :duration (= ?duration 3)
   :condition (and (ball ?obj) (room ?room) (gripper ?gripper)
                 (carry ?obj ?gripper) (at-robby ?room))
    :effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))))