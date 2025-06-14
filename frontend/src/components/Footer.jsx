import { Building2, Mail, Phone, MapPin } from "lucide-react";
import { FaFacebookF, FaLinkedinIn, FaYoutube } from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="bg-black text-white py-14">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-10">
          {/* Left: Company Info */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold">WH REALTORS</h3>
            <ul className="text-base space-y-1 text-gray-300">
              <li className="flex items-center space-x-3">
                <Phone className="w-5 h-5" />
                <span className="text-blue-400">+91 00000 00000</span>
              </li>
              <li className="flex items-center space-x-3">
                <Mail className="w-5 h-5" />
                <span className="text-blue-400">info@whrealtors.in</span>
              </li>
              <li className="flex items-center space-x-3">
                <MapPin className="w-5 h-5" />
                <span className="text-gray-300">Address Goes Here</span>
              </li>
            </ul>
          </div>

          {/* Right: Social + Copyright */}
          <div className="flex flex-col items-start md:items-end gap-6">
            <p className="text-base text-gray-400">
              © Copyright 2025. All Rights Reserved by WH Realtors
            </p>
            <div className="flex space-x-5">
              <a href="#" aria-label="Facebook" className="bg-gray-800 hover:bg-white hover:text-black text-white p-3 rounded-full transition">
                <FaFacebookF size={20} />
              </a>
              <a href="#" aria-label="LinkedIn" className="bg-gray-800 hover:bg-white hover:text-black text-white p-3 rounded-full transition">
                <FaLinkedinIn size={20} />
              </a>
              <a href="#" aria-label="YouTube" className="bg-gray-800 hover:bg-white hover:text-black text-white p-3 rounded-full transition">
                <FaYoutube size={20} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
