import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

const ProjectCard = ({ project }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      viewport={{ once: true, amount: 0.3 }}
    >
      <Link
        to={`/projects/${project.id}`}
        className="relative group block rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 bg-gray-900"
      >
        {/* Image */}
        <div className="aspect-[4/3] overflow-hidden">
          <img
            src={project.image}
            alt={project.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>

        {/* Hover Overlay */}
        <div className="absolute bottom-4 left-4 right-4 bg-white dark:bg-gray-900 rounded-xl p-4 shadow-md opacity-0 group-hover:opacity-100 translate-y-6 group-hover:translate-y-0 transition-all duration-300 ease-out flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 font-medium mb-1">{project.title}</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">{project.price || '225.000'}</p>
          </div>
          <div className="text-sm text-blue-600 font-medium flex items-center">
            View <ArrowRight className="ml-1 w-4 h-4" />
          </div>
        </div>

        {/* Title - visible when not hovered */}
        <div className="absolute bottom-0 left-0 w-full py-3 px-4 text-white text-sm font-medium bg-gradient-to-t from-black/60 to-transparent rounded-b-2xl group-hover:opacity-0 transition-opacity duration-300">
          {project.title}
        </div>
      </Link>
    </motion.div>
  );
};

export default ProjectCard;
