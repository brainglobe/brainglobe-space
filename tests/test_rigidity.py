import numpy as np
import pytest
from brainglobe_space import AnatomicalSpace
from brainglobe_space.functions import map_to, map_stack_to, transformation_matrix_to, transform_points_to

def test_rigidity_check():
    # Rigid transformation: asl -> sla (rotation)
    # Det = 1
    asl = AnatomicalSpace("asl")
    sla = AnatomicalSpace("sla")
    
    # Should work fine
    asl.map_to(sla)
    asl.map_to(sla, check_rigid=True)
    
    # Non-rigid transformation: asl -> sal (swap s and a)
    # Det = -1
    sal = AnatomicalSpace("sal")
    
    with pytest.raises(ValueError, match="is non-rigid"):
        asl.map_to(sal)
        
    with pytest.raises(ValueError, match="is non-rigid"):
        asl.map_to(sal, check_rigid=True)
        
    # Should work if check_rigid=False
    asl.map_to(sal, check_rigid=False)

def test_rigidity_check_helper_functions():
    # Helper functions in functions.py
    source = "asl"
    target = "sal" # non-rigid
    
    with pytest.raises(ValueError, match="is non-rigid"):
        map_to(source, target)
        
    map_to(source, target, check_rigid=False)
    
    stack = np.zeros((10, 10, 10))
    with pytest.raises(ValueError, match="is non-rigid"):
        map_stack_to(source, target, stack)
        
    map_stack_to(source, target, stack, check_rigid=False)
    
    with pytest.raises(ValueError, match="is non-rigid"):
        transformation_matrix_to(source, target, shape=(10, 10, 10))
        
    transformation_matrix_to(source, target, shape=(10, 10, 10), check_rigid=False)
    
    points = np.array([[1, 2, 3]])
    with pytest.raises(ValueError, match="is non-rigid"):
        transform_points_to(source, target, points, shape=(10, 10, 10))
        
    transform_points_to(source, target, points, shape=(10, 10, 10), check_rigid=False)

def test_rigidity_check_decorator():
    # Test that the to_target decorator passes check_rigid correctly
    asl = AnatomicalSpace("asl")
    
    # map_stack_to uses to_target
    stack = np.zeros((10, 10, 10))
    with pytest.raises(ValueError, match="is non-rigid"):
        asl.map_stack_to("sal", stack)
        
    asl.map_stack_to("sal", stack, check_rigid=False)
