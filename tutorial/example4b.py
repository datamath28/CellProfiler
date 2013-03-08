'''<b>Example4</b> Object processing
<hr>
'''

import cellprofiler.cpmodule as cpm
import cellprofiler.measurements as cpmeas
import cellprofiler.objects as cpo
import cellprofiler.settings as cps

#
# cellprofiler.cpmath.cpmorphology has many useful image processing algorithms.
# 
# skeletonize_labels performs the skeletonization (medial axis transform) for
# each labeled object in a labels matrix. It can skeletonize thousands of
# objects in an image almost as rapidly as skeletonizing a single object
# of the same complexity.
#
from cellprofiler.cpmath.cpmorphology import skeletonize_labels

class Example4b(cpm.CPModule):
    module_name = "Example4b"
    variable_revision_number = 1
    category = "Object Processing"
    
    def create_settings(self):
        #
        # The ObjectNameSubscriber is aware of all objects published by
        # modules upstream of this one. You use it to let the user choose
        # the objects produced by a prior module.
        #
        self.input_objects_name = cps.ObjectNameSubscriber(
            "Input objects", "Nuclei")
        #
        # The ObjectNamePublisher lets downstream modules know that this
        # module will produce objects with the name entered by the user.
        #
        self.output_objects_name = cps.ObjectNameProvider(
            "Output objects", "Skeletons")
        
    def settings(self):
        return [self.input_objects_name, self.output_objects_name]
    
    def run(self, workspace):
        #
        # This is unfortunate... sorry. example4b.py is imported during the
        # import of cellprofiler.modules. This means that the import of
        # cellprofiler.modules.identify can't be done in this module's import
        #
        import cellprofiler.modules.identify as I
        #
        # The object_set keeps track of the objects produced during a cycle
        #
        # Crucial methods:
        #
        # object_set.get_objects(name) returns an instance of cpo.Objects
        #
        # object_set.add(objects, name) adds objects with the given name to
        #           the object set
        #
        #
        # Create objects in three steps:
        #     make a labels matrix
        #     create an instance of cpo.Objects()
        #     set cpo.Objects.segmented = labels matrix
        #
        # You can be "nicer" by giving more information, but this is not
        # absolutely necessary. See subsequent exercises for how to be nice.
        #     
        object_set = workspace.object_set
        input_objects = object_set.get_objects(self.input_objects_name.value)
        labels = skeletonize_labels(input_objects.segmented)
        output_objects = cpo.Objects()
        output_objects.segmented = labels
        output_objects_name = self.output_objects_name.value
        object_set.add_objects(output_objects, output_objects_name)
        
        measurements = workspace.measurements
        n_objects = output_objects.count
        I.add_object_count_measurements(measurements, output_objects_name,
                                        n_objects)
        I.add_object_location_measurements(
            measurements, output_objects_name, labels, n_objects)
        
    def get_measurement_columns(self, pipeline):
        import cellprofiler.modules.identify as I
        return I.get_object_measurement_columns(
            self.output_objects_name.value)
    
    def get_categories(self, pipeline, object_name):
        import cellprofiler.modules.identify as I
        if object_name == cpmeas.IMAGE:
            return [I.C_COUNT]
        elif object_name == self.output_objects_name:
            return [I.C_LOCATION]
        return []
    
    def get_measurements(self, pipeline, object_name, category):
        import cellprofiler.modules.identify as I
        if object_name == cpmeas.IMAGE and category == I.C_COUNT:
            return [self.output_objects_name.value]
        if object_name == self.output_objects_name and category == I.C_LOCATION:
            return [I.FTR_CENTER_X, I.FTR_CENTER_Y]