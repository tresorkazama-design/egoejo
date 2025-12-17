import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';

export const NotFound = () => {
  const { language } = useLanguage();
  
  return (
    <div className="not-found-page" data-testid="not-found-page">
      <div className="text-center py-12">
        <h1 className="text-6xl font-bold mb-4">404</h1>
        <h2 className="text-2xl font-bold mb-4">{t("common.not_found", language)}</h2>
        <p className="text-gray-600 mb-6">
          {t("common.not_found_desc", language)}
        </p>
        <Link to="/" className="bg-blue-600 text-white px-6 py-3 rounded inline-block">
          {t("common.back_home", language)}
        </Link>
      </div>
    </div>
  );
};

export default NotFound;

