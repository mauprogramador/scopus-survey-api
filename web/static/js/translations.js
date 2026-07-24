// Translations Texts
const translationTexts = {
  'en-US': {
    S01: 'CSV downloaded successfully.',
    S02: 'Combinations found successfully.',
    S03: 'Articles found successfully.',
    W01: 'This option exceeds the available API Key request quotas.',
    W02: 'There are no remaining API Key request quotas.',
    W03: 'Dealing with this high total of results will take some time.',
    W04: (used) => `This will consume ${used} of your \
      remaining API Key request quotas.`,
    W05: 'We can only retrieve the results up to the \
      available API Key request quotas.',
    W06: 'There are no remaining API Key request quotas,\
      nor valid options with results above zero.',
    E01: (wildcard) => `Wildcard '${wildcard}' must have text after it.`,
    E02: (wildcard) => `Wildcard '${wildcard}' must have text before it.`,
    E03: (wildcard) =>
      `Wildcard '${wildcard}' must have text before or after it.`,
    E04: 'Unmatched double quotation marks.',
    E05: 'Quoted text cannot be empty.',
    E06: 'Quoted text cannot contain only spaces.',
    E07: 'Unmatched curly braces.',
    E08: 'Braced text cannot be empty.',
    E09: 'Braced text cannot contain only spaces.',
  },
  'pt-BR': {
    S01: 'Download do CSV com sucesso.',
    S02: 'Combinações encontradas com sucesso.',
    S03: 'Artigos encontradas com sucesso.',
    W01: 'Excede a cota de solicitações disponível para a Chave de API.',
    W02: 'Não há mais solicitações disponíveis para a Chave de API.',
    W03: 'Lidar com esse grande número de resultados levará algum tempo.',
    W04: (used) => `Isso consumirá ${used} das suas cotas restantes \
      de requisições da Chave de API.`,
    W05: 'Só podemos obter resultados até o limite das cotas de solicitação\
      de Chave de API disponíveis',
    W06: 'Não há cotas restantes de solicitação de Chave de API\
      nem opções válidas com resultados acima de zero.',
    E01: (wildcard) =>
      `O caractere curinga '${wildcard}' deve ter texto após ele.`,
    E02: (wildcard) =>
      `O caractere curinga '${wildcard}' deve ter texto antes dele.`,
    E03: (wildcard) =>
      `O caractere curinga '${wildcard}' deve ter texto antes ou depois dele.`,
    E04: 'Aspas duplas não correspondentes.',
    E05: 'Texto entre aspas não pode estar vazio.',
    E06: 'Texto entre aspas não pode conter apenas espaços.',
    E07: 'Chaves não correspondentes.',
    E08: 'Texto entre chaves não pode estar vazio.',
    E09: 'Texto entre chaves não pode conter apenas espaços.',
  },
};

// Error Feedbacks
const errorFeedbacks = {
  'en-US': {
    valueMissing: 'Fill in this required field',
    typeMismatch: 'Value with invalid type',
    tooLong: 'Value too long',
    tooShort: 'Value too short',
    patternMismatch: 'Value with invalid pattern',
    rangeOverflow: 'Value greater than maximum',
    rangeUnderflow: 'Value less than minimum',
    noInterval: 'Interval must be at least one year',
    startyear: 'Start Year must be less than End Year',
    endyear: 'End Year must be greater than Start Year',
    multipleSpaces: 'Multiple consecutive spaces are not allowed',
  },
  'pt-BR': {
    valueMissing: 'Preencha este campo obrigatório',
    typeMismatch: 'Valor com tipo inválido',
    tooShort: 'Valor muito curto',
    tooLong: 'Valor muito longo',
    patternMismatch: 'Valor com padrão inválido',
    rangeOverflow: 'Valor maior que o máximo',
    rangeUnderflow: 'Valor menor que o mínimo',
    noInterval: 'Intervalo deve ser de pelo menos um ano',
    startyear: 'Ano inicial deve ser menor que o ano final',
    endyear: 'Ano final deve ser maior que o ano inicial',
    multipleSpaces: 'Múltiplos espaços consecutivos não são permitidos',
  },
};

const detailsGroupLabels = {
  'en-US': {
    'API Key': {
      'x-api-key': 'API Key',
    },
    'Search API (Quota)': {
      'x-search-limit': 'Limit',
      'x-search-remaining': 'Remaining',
      'x-search-reset': 'Reset',
    },
    'Abstract API (Quota)': {
      'x-abstract-limit': 'Limit',
      'x-abstract-remaining': 'Remaining',
      'x-abstract-reset': 'Reset',
    },
    Survey: {
      'x-keywords': 'Keywords',
      'x-combination': 'Combination',
      'x-scopus-total': 'Scopus total',
      'x-total-retrieved': 'Total retrieved',
      'x-total-final': 'Final total',
      'x-loss': 'Loss',
      'x-pages-count': 'Pages count',
      'x-items-per-page': 'Items per page',
      'x-process-time': 'Process time',
    },
  },
  'pt-BR': {
    'Chave de API': {
      'x-api-key': 'Chave de API',
    },
    'Search API (Cota)': {
      'x-search-limit': 'Limite',
      'x-search-remaining': 'Restante',
      'x-search-reset': 'Redefinição',
    },
    'Abstract API (Cota)': {
      'x-abstract-limit': 'Limite',
      'x-abstract-remaining': 'Restante',
      'x-abstract-reset': 'Redefinição',
    },
    Levantamento: {
      'x-keywords': 'Palavras-chave',
      'x-combination': 'Combinação',
      'x-scopus-total': 'Total Scopus',
      'x-total-retrieved': 'Total obtido',
      'x-total-final': 'Total final',
      'x-loss': 'Perda',
      'x-pages-count': 'Número de páginas',
      'x-items-per-page': 'Itens por página',
      'x-process-time': 'Tempo de processamento',
    },
  },
};

export { translationTexts, errorFeedbacks, detailsGroupLabels };
